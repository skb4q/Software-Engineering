#!/usr/bin/python3
import re
from collections import defaultdict
import copy


def remove_endl(line):
    result = ""
    for ch in line:
        if ch != '\n' and ch != '\r':
            result += ch
    return result


def init():
    with open("RealAcademiaEspanola-DiccionarioLlengueaEspanola.txt",
              encoding='UTF-8') as f:
        espDict = defaultdict(list)
        p_of_speech = [
                "m.", "verb.", "adj.", "V.",
                "f.", "var.", "abbr.", "prefix.",
                "colloq.", "symb.", "adv.", "naut.",
                "prep.", "mus.", "int.", "comb.",
                "predic.", "aeron.", "contr.", "slg.",
                "chem.", "attrib.", "ist.", "conj.",
                "pron.", "past.", "usu.", "biol.",
                "derog.", "esp.", "vulg.", "pastpart.",
                "coarseslg.", "unst.", "can.", "noun."
                ]
        part_of_speech = frozenset(p_of_speech)
        dicstr = f.read()
        defs = []
        entries = []
        perword = defaultdict(list)
        entries = dicstr.split('>')
        for entry in entries:
            pala, sep, definition = entry.partition('.')
            front, sep, definition = definition.partition('1.')
            definition = sep + definition
            regex = re.compile(r'(\d+. )')
            defs = regex.split(definition)
            for d in defs:
                words = d.split()
                for word in words[0:3]:
                    if word in part_of_speech:
                        if word == 'f.' or word == 'm.':
                            word = 'noun.'
                        perword[word[:-1]].append(remove_endl(d))
            espDict[pala] = copy.deepcopy(perword)
            perword.clear()
    return dict(espDict)


if __name__ == "__main__":
    yn = None
    pos = None
    defn = None
    espDict = {}
    espDict = init()
    while yn != 'y':
        word = input("word to define: ")
        yn = None
        while yn != 'y' and yn != 'n':
            yn = input("would you like to give a part of speech? y/n ")
        if yn == 'y':
            for d in espDict[word]:
                print(d)
            pos = input("part of speech: ")
            yn = None
            while yn != 'y' and yn != 'n':
                yn = input("would you like to give an index? y/n ")
            if yn == 'y':
                defn = input("index: ")
        try:
            if pos and defn:
                print('\n' + espDict[word][pos][int(defn)])
            elif pos:
                for i in espDict[word][pos]:
                    print(i + '\n')
            else:
                for i in espDict[word]:
                    for j in espDict[word][i]:
                        print(j)
        except Exception:
            print("\nNOT FOUND")
        yn = None
        while yn != 'y' and yn != 'n':
            yn = input("\nquit? y/n ")
