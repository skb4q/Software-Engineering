import re
import string
import copy
import matplotlib.pyplot as plt
from anytree import Node, RenderTree, AsciiStyle
from anytree.exporter import DotExporter
import spacy
import multiprocessing
from multiprocessing import Pool
nlp = spacy.load('en_core_web_sm')

entryDict = {}
nodes = []

#removes text inside brackets
def remove_text_inside(text, brackets="()[]"):
    count = [0] * (len(brackets) // 2) # count open/close brackets
    saved_chars = []
    for character in text:
        for i, b in enumerate(brackets):
            if character == b: # found bracket
                kind, is_close = divmod(i, 2)
                count[kind] += (-1)**is_close # `+1`: open, `-1`: close
                if count[kind] < 0: # unbalanced bracket
                    count[kind] = 0  # keep it
                else:  # found bracket to remove
                    break
        else: # character is not a [balanced] bracket
            if not any(count): # outside brackets
                saved_chars.append(character)
    return ''.join(saved_chars)

def remove_end(text):
    new_text = ""
    for ch in text:
        if ord(ch) == 127:
            return new_text
        else:
            new_text += ch
    return new_text

def remove_num(word):
    result = ''.join([i for i in word if not i.isdigit()])
    return result

def remove_notalpha(line):
    result = ''.join([i for i in line if i.isalpha() or i == ' '])
    return result

def remove_double_space(line):
    lastch = ''
    result = ""
    for ch in line:
        if not (ch == ' ' and lastch == ' '):
            lastch = ch
            result += ch
        else:
            lastch = ch
    return result

def remove_endl(line):
    result = ""
    for ch in line:
        if ch != '\n' and ch != '\r':
            result += ch
    return result

def print_last_ascii(line):
    lastCh = ''
    for ch in line:
        lastCh = ch
    return ord(lastCh)

#changes multiword parts of speech into single word part of speech
def change_part_of_speech(line):
    line = re.sub('past part', 'pastpart', line.rstrip())
    line = re.sub('us var', 'usvar', line.rstrip())
    line = re.sub('coarse slg','coarseslg', line.rstrip())
    return line

#take a line and format it
def groom_text(line):
    #next several lines just format the dictionary
    line = line.encode('ascii', 'ignore').decode('ascii')
    line = remove_text_inside(line, brackets="()[]") 
    line = remove_end(line)
    line = remove_notalpha(line)
    line = remove_double_space(line)
    line = line.lower()
    #maybe good to just alter the dictionary but for now I am going to try 
    #and do that as little as possible
    line = change_part_of_speech(line)
    #words = re.split("[ ,!?;:]", line)
    #words = list(filter(None, words))
    return line

#read the dicitonary and put it in a python dictionary
def read_data():
    cnt = 0
    p_of_speech = [
        "n", "v", "adj","npl",
        "pl","var","abbr","prefix",
        "colloq","symb","adv","naut",
        "prep","adj","mus","int","comb",
        "predic","aeron","contr","slg",
        "chem","attrib","ist","conj",
        "pron","adv","past","usu","biol", 
        "derog","esp","usvar","pastpart",
        "coarseslg","unst", "can", "austral"
        ]
    PART_OF_SPEECH = frozenset(p_of_speech)
    with open("dictionary.txt", encoding='UTF-8') as dictFile:
        for line in dictFile:
            cnt = cnt + 1
            delim = False
            key = ""
            line = groom_text(line)
            tokens = nlp(line)
            for token in tokens:
                if not delim:
                    if token.text in PART_OF_SPEECH:
                        delim = True
                        entryDict.update({key:([],"",0)})
                    elif token.is_alpha and not token.is_stop:
                        key += token.text
                elif delim and not token.is_stop and token.text not in PART_OF_SPEECH:
                    entryDict[key][0].append(token.lemma_)
        dictFile.close()
    return cnt

def tree_define_itr(initItem):
    #variables
    undef = 0
    lvl = 1 
    maxWidth = 0
    numberNodes = 0
    onThisLvl = 0
    onPrevLvl = 0
    prntIndex = 0 
    prnt = []
    tree = []
    todefine = []
    defined = []
    definition = []
    #init get def of root
    try:
        todefine = copy.deepcopy(entryDict[initItem][0])
        prnt.append(len(todefine))
        tree.append(Node(initItem, parent = None, level = 0))
        defined.append(initItem)
        onPrevLvl = len(todefine)
    except:
        print("ERROR: Tree initialization failed.")
        return tree
    #build the rest of the tree
    for item in todefine:
        #increment level
        if onPrevLvl == 0:
            lvl = lvl + 1
            #set the maximum width of the tree
            if onThisLvl > maxWidth:
                maxWidth = onThisLvl
            onPrevLvl = onThisLvl
            onThisLvl = 0
        #increment index
        while prntIndex < len(prnt) and prnt[prntIndex] < 1:
            prntIndex = prntIndex + 1
        #2018-08-20 experimenting with leaving childless nodes out of tree
        #add node to tree
        tree.append(Node(item, parent = tree[prntIndex], level = lvl))
        if item not in defined:
            #appending definitions here
            try:
                definition = copy.deepcopy(entryDict[item][0])
            except:
                undef = undef + 1
                #print("UNDEFINED: ", item)
            onThisLvl += len(definition)
            prnt.append(len(definition))
            todefine.extend(list(definition))
            defined.append(item)
        else:
            prnt.append(0)
        prnt[prntIndex] = prnt[prntIndex] - 1
        onPrevLvl = onPrevLvl - 1
        definition.clear()
    return tree, maxWidth, lvl, undef

#generates a histogram for number of nodes created
def generate_hist(nodeCnt):
    plt.hist(nodeCnt)
    plt.title("Number of Nodes per Word")
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    plt.savefig("histogram.png")

def process(word):
    tree = []
    #create the tree and read relevent data
    tree, width, depth, undef = tree_define_itr(word)
    nodeCnt = len(tree)
    #record nodes created
    line = str(word) + " " + str(nodeCnt) + " " + str(width) + " " + str(depth) + " " + str(undef) + "\n"
    numNodes.write(line)
    print(line)
    #DotExporter(tree[0]).to_picture(word+".png") 
    #append the node count to the list so the histo can be made
    nodes.append(nodeCnt)
    #print(RenderTree(tree[0],style=AsciiStyle()))
    nodeCnt = 0
    width = 0
    depth = 0
    undef = 0
    tree.clear	

if __name__ == '__main__':
    procs = multiprocessing.cpu_count()
    #read the dictionary
    cnt = read_data()
    print("Dictionary has " + str(cnt) + " entries.") 
    #open file to record number of nodes created
    numNodes = open("numNodes.txt", "w")
    numNodes.write("word nodes width depth undefined")
    print("word nodes width depth undefined")
    #generate data for each word in the dictionary 
    with Pool(procs) as pool:
        pool.map(process, entryDict)
    pool.join()
    numNodes.close()
    #generate a histogram of the number of nodes created for each word
    #generate_hist(nodes)
    #RenderTreeGraph(tree[0]).to_picture("cat.png")
    #print_all(tree)
