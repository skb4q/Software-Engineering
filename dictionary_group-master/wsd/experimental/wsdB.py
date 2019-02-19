#!/usr/bin/python3
import spacy
from pywsd.lesk import simple_lesk, cosine_lesk
from nltk.corpus import wordnet as wn


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

def split_syn(answer):
    sense = str(answer)
    sense = sense.replace("Synset(", "")
    sense = ''.join(c for c in sense if c not in '()\' ')
    sense = sense.split(".")
    return sense

# load english dict
nlp = spacy.load('en')
sentence = []
# load book - may not be needed in real implementation
with open('./helpfulfriends.txt', 'r') as content_file:
    context = content_file.read()
    sentence = context.split('.')
# for s in sentence:
#    answers = disambiguate(s, adapted_lesk, keepLemmas=False)

# what I was doing before
context = remove_notalpha(context)
# lemmatize the context
doc = nlp(context)
for token in doc:
    print("")
    if ' ' not in token.text and not token.is_stop and token.pos_ != '-PRON-':
        try:
            con = ''.split(context)
            for word in con:
                if word == token.text:
                    context = token.text + " "
            answer = simple_lesk(context, token.text, pos_convert(token.pos_))
            print(answer)
            if not answer:
                continue
        except Exception:
            continue

        sense = split_syn(answer)
        print(sense[0] + " " + token.lemma_)
        if ((sense[0] != token.lemma_ or
             int(sense[2]) > 4) and token.pos_ != 'PROPN'):
            try:
                cosans = cosine_lesk(context, token.text,
                                     pos_convert(token.pos_))
                if(check_def(context, cosans.definition()) >
                   check_def(context, answer.definition())):
                    answer = cosans
                if ((sense[0] != token.lemma_ or
                     int(sense[2]) > 4) and token.pos_ != 'PROPN'):
                    answer = wn.synset(token.lemma_ + '.' +
                                       pos_convert(token.pos_) +
                                       '.01')
                    print("unlikely sense detected - new sense:")
                    print(answer)
            except Exception:
                pass
        # needs to look for beginning of sentence
        if (token.pos_ == 'PROPN'):
                print(token.text + " is a proper noun.")
        elif answer:
            print("word :" + token.lemma_ + "\n" +
                  "def :" + answer.definition())
            # print("word :" + token.lemma_ + " " + str(answer))
