#!/usr/bin/python3
import spacy
import json
import requests
from pywsd.lesk import simple_lesk, cosine_lesk
from nltk.corpus import wordnet as wn
#from espdict import espdict

def remove_notalpha(line):
    line = line.replace('\n', ' ')
    result = ''.join([i for i in line if i.isalpha() or i == ' ' or i == '\n'])
    return result


def pos_convert(pos):
    pos_dict = {'NOUN': 'n', 'VERB': 'v', 'ADJ': 'a'}
    try:
        return pos_dict[pos]
    except Exception:
        return pos


def check_def(context, definition):
    definition = nlp(definition)
    pnt = 100/len(definition)
    score = 0
    context.split()
    for word in definition:
        if not word.is_stop and word.text in context:
            score = score + pnt
    return score

# load english dict
nlp = spacy.load('en')
esp = {}
esp = espdict.create()
lang = "spa"
sentence = []
# load book - may not be needed in real implementation
with open('../../text/helpfulfriends.txt', 'r') as content_file:
    context = content_file.read()
    sentence = context.split('.')
# for s in sentence:
#    answers = disambiguate(s, adapted_lesk, keepLemmas=False)

# what I was doing before
context = remove_notalpha(context)
# lemmatize the context
doc = nlp(context)
for token in doc[0:10]:
    print("")
    if ' ' not in token.text and not token.is_stop and token.pos_ != '-PRON-':
        try:
            con = ''.split(context)
            for word in con:
                if word == token.text:
                    context = token.text + " "
            answer = simple_lesk(context, token.text, 
                                pos_convert(token.pos_))
            cosans = cosine_lesk(context, token.text, 
                                pos_convert(token.pos_))
            if(check_def(context, cosans.definition()) >
               check_def(context, answer.definition())):
                print("using cosine lesk")
                answer = cosans
            print(answer)
            if not answer:
                continue
        except Exception:
            continue
        sense = str(answer)
        sense = sense.replace("Synset(", "")
        sense = ''.join(c for c in sense if c not in '()\' ')
        sense = sense.split(".")
        print(sense[0] + " " + token.lemma_)
        if ((sense[0] != token.lemma_ or
             int(sense[2]) > 4) and token.pos_ != 'PROPN'):
            try:
                answer = wn.synset(token.lemma_ + '.' +
                                   pos_convert(token.pos_) +
                                   '.01')
                print("unlikely sense detected - new sense:")
                print(answer)
            except Exception:
                pass

        #this should use the spa or arb word given 
        getstr = "https://glosbe.com/gapi/translate?from="+lang+"&dest=eng&format=json&phrase="+"jugar"+"&pretty=true"
        if lang == 'spa':
            lang = 'es'
        if lang == 'arb':
            lang = 'ar'
        response = requests.get(getstr)
        indef = json.loads(response.text)
        maximum = 0
        meaning = indef['tuc'][0]['meanings'][0]['text']
        if len(indef['tuc']) > 0:
            for tuc in indef['tuc']:
                try:
                    if tuc['phrase']['text'] == token.lemma_:
                        print("right phrase")
                        esptemp = ""
                        for m in tuc['meanings']:
                            print(m['text'])
                            if m['language'] == lang and len(m['text']) > len(esptemp):
                                meaning = m['text']
                except KeyError:
                    pass
            print(meaning) 
        # needs to look for beginning of sentence
        if (token.pos_ == 'PROPN'):
                print(token.text + " is a proper noun.")
        elif answer:
            print("word :" + token.lemma_ + "\n" +
                  "def :" + answer.definition())
            # print("word :" + token.lemma_ + " " + str(answer))
