import nltk
import os
from nltk.corpus import words, brown
from preprocess import PreProcess
import spacy
import json
import time
from spellchecker import SpellChecker
import multiprocessing

def suggestions(word):
    spell = SpellChecker()
    errorList = {}
    if not word.isupper() and not any(char.isdigit() for char in word):
        candidateWords = spell.candidates(word)
        errorList[word] = {
            "correction": max(candidateWords, key=spell.word_probability),
            "suggestion": spell.candidates(word)
        }
    return errorList

def findErrors(wordList, thistime):
    spell = SpellChecker()
    errorCount = 0
    errorList = {}

    misspelled = [word for word in spell.unknown(wordList)]

    pool = multiprocessing.Pool(processes=4)
    errorList = pool.map(suggestions, misspelled)
    pool.close()
    # for word in misspelled:
    #     # Get the one `most likely` answer
    #     if not word.isupper() and not any(char.isdigit() for char in word):
    #         candidateWords = spell.candidates(word)
    #         errorList[word] = {
    #             "correction": max(candidateWords, key=spell.word_probability),
    #             "suggestion": spell.candidates(word)
    #         }
    # print("suggestion Time: --- %s seconds ---\n\n\n\n\n" % (time.time() - thistime))
        # print(spell.word_probability(word))
    filterdList = [dict for dict in errorList if len(dict) > 0]
    return {
        "errorCount": len(filterdList),
        "errorList": filterdList
    }

# def findErrors(wordList):
#     misspelled = [word for word in wordList if (word not in words.words() and not any(char.isdigit() for char in word) and not word.isupper())]
#     initials = set([i[0] for i in misspelled if i[0]])
#
#     suggestionWordList = {}
#     for i in initials:
#         suggestionWordList[i] = [word for word in words.words() if word[0] == i]
#
#
#     errorList = {}
#     for word in misspelled:
#         suggestions = [((nltk.edit_distance(word, a)), a) for a in suggestionWordList[word[0]]]
#         sortedSuggestion = sorted(suggestions, key=lambda x: x[0])[:4]
#         errorList[word] = {
#             "correction": sortedSuggestion[0][1],
#             "suggestion": [word[1] for word in sortedSuggestion]
#         }
#     return {
#             "errorCount": len(errorList),
#             "errorList": errorList
#         }

# print(lemmatizeSentence("The stripeed bats are hanging on their feet for better"))
start_time = time.time()
thisTime = start_time
files = []
dataFolder = os.path.dirname(os.path.abspath(__file__)) + "/data"
count = 0
for i in os.listdir(dataFolder):
    if i.endswith('.txt'):
        # if count != 3:
        #     count = count + 1
        #     continue
        thisFile = os.path.join(dataFolder, i)
        reflection = open(thisFile, "r", encoding='utf8')

        print("\n\n")

        print(os.path.basename(reflection.name))
        processData = PreProcess(reflection.read())

        wordList = processData.getWordList(True, True)
        # print("WordList Time: --- %s seconds ---\n\n\n\n\n" % (time.time() - thisTime))
        withoutContractions = processData.removeContractions(wordList)
        # print("WordList Time: --- %s seconds ---\n\n\n\n\n" % (time.time() - thisTime))
        # print(withoutContractions)
        lemmaWordList = processData.lemmatizeWordList(withoutContractions)
        print("WordList Time: --- %s seconds ---\n\n\n\n\n" % (time.time() - thisTime))

        spellErrors = findErrors(lemmaWordList, thisTime)

        print("File: " + os.path.basename(reflection.name))
        print("Words calculated: " + str(len(wordList)))
        print("Error Word Count: " + str(spellErrors['errorCount']))
        print("ErrorWord\t\t\tCorrection\t\t\tSuggestions")
        print("---------\t\t\t----------\t\t\t-----------")
        for eachError in spellErrors["errorList"]:
            for key,value in eachError.items():
                print(key + "\t\t\t" + value["correction"] + "\t\t\t" + ", ".join(value["suggestion"]))
        # for key,value in spellErrors["errorList"].items():
        #     print(key + "\t\t\t" + value["correction"] + "\t\t\t" + ", ".join(value["suggestion"]))

        print("Total Time: --- %s seconds ---\n\n\n\n\n" % (time.time() - thisTime))
        thisTime = time.time()
        # result.close()
        reflection.close()
    count = count + 1
print("--- %s seconds ---" % (time.time() - start_time))
