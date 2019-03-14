import nltk
from nltk import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet, words
from nltk.corpus import stopwords
from nltk.probability import FreqDist
import string
import json
import re
import pyphen
import spacy
import time
import os
import multiprocessing

class PreProcess:
    completeText = ""
    def __init__(self, text):
        self.text = text

    def getContractionList(self):
        with open('contractions.json') as f:
            contractions = json.load(f)
        return [key for key, value in contractions.items()]

    def getFullText(self):
        with open('contractions.json') as f:
            contractions = json.load(f)
        reQuery = re.compile('(%s)' % '|'.join(contractions.keys()))
        def replace(match):
            return contractions[match.group(0)]
        self.completeText = reQuery.sub(replace, self.text.lower())
        return self.completeText

    def get_wordnet_pos(self, tag):
        """Map POS tag to first character lemmatize() accepts"""
        # tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {"J": wordnet.ADJ,
                    "N": wordnet.NOUN,
                    "V": wordnet.VERB,
                    "R": wordnet.ADV}

        return tag_dict.get(tag, wordnet.NOUN)

    def eachLemma(self, tuple):
        lemmatizer = WordNetLemmatizer()
        if lemmatizer.lemmatize(tuple[0], self.get_wordnet_pos(tuple[1])) == tuple[0]:
            return tuple

    def wordnetLemma(self, wordList):
        newList = []
        pool = multiprocessing.Pool(processes=4)
        newList = pool.map(self.eachLemma, wordList)
        pool.close()
        # for word in wordList:
        #     if lemmatizer.lemmatize(word[0], self.get_wordnet_pos(word[1])) == word[0]:
        #         newList.append(word)
        return newList


    def lemmatizeWordList(self, wordList):
        nlp = spacy.load('en_core_web_sm', disable=['parser', 'tagger', 'ner'])
        lemmaWordList = []
        for word in wordList:
            doc = nlp(word)
            lemmaWord = [token.lemma_ for token in doc]
            lemmaWordList = lemmaWordList + [eachLemma.replace('\ufeff', '') for eachLemma in lemmaWord]
        return lemmaWordList

    def stringToList(self, stop=False, splitHyphen=False):
        wordList = word_tokenize(self.text)
        taggedList = nltk.pos_tag(wordList)
        punctuationList = """!"#$%*+,.:;[]()<=>?@^_`{|}~"""
        punctuationMap = str.maketrans('', '', punctuationList)
        stripped = [(w[0].translate(punctuationMap), w[1]) for w in taggedList if w[0].translate(punctuationMap) != ""]
        newList = []
        for eachWord in stripped:
            eachNoBrackList = re.compile('[\[\]\(\)—/]').split(eachWord[0])
            eachNoBrackList = nltk.pos_tag(eachNoBrackList) if len(eachNoBrackList) > 1 else [eachWord]
            for listword in eachNoBrackList:
                eachNoQuoteWord = listword[0].strip("\'|\"|\”|\“|\’")
                # eachNoQuoteWord = eachNoQuoteWord.replace("\'s", "")
                eachNoHyphenWord = eachNoQuoteWord.strip("\-|\–")
                if splitHyphen and "-" in eachNoHyphenWord:
                    hyphenList = [word if word.isupper() else word.lower() for word in eachNoHyphenWord.split('-')]
                    newList = newList + nltk.pos_tag(hyphenList)
                elif eachNoHyphenWord != "":
                    newList.append((eachNoHyphenWord if eachNoHyphenWord.isupper() else eachNoHyphenWord.lower(), listword[1]))

        usefulWords = [(word[0], word[1]) for word in newList if word[0] not in stopwords.words("english")]
        if stop:
            return usefulWords
        else:
            return newList

    def getWordList(self, text, stop, splitHyphen=False):
        wordList = self.text.split()
        punctuationList = """!"#$%*+,.:;<=>?@^_`{|}~"""
        punctuationMap = str.maketrans('', '', punctuationList)
        stripped = [w.translate(punctuationMap) for w in wordList]

        # replace ()/ with spliting the word and add to the main list
        # strip '"- from start or end of the word.
        newList = []
        parenRegex = r"\(?.*?\)?"
        bothAposRegex = r"(\"?.*?\"?)|(\'?.*?\'?)"
        for eachWord in stripped:
            eachNoBrackList = re.compile('[\[\]\(\)—/]').split(eachWord)
            for listword in eachNoBrackList:
                eachNoQuoteWord = listword.strip("\'|\"|\”|\“|\’")
                eachNoQuoteWord = eachNoQuoteWord.replace("\’", "\'")
                eachNoHyphenWord = eachNoQuoteWord.strip("\-|\–")
                if splitHyphen and "-" in eachNoHyphenWord:
                    hyphenList = [word if word.isupper() else word.lower() for word in eachNoHyphenWord.split('-')]
                    newList = newList + hyphenList
                elif eachNoHyphenWord != "":
                    newList.append(eachNoHyphenWord if eachNoHyphenWord.isupper() else eachNoHyphenWord.lower())

        wordTag = nltk.pos_tag(newList)

        usefulWords = [word for word in newList if word not in stopwords.words("english")]
        if stop:
            return usefulWords
        else:
            return newList

    def removeContractionsTuple(self, wordList):
        newList = []
        for word in wordList:
            # if word in self.getContractionList()
            if any(contraction in word[0] for contraction in self.getContractionList()):
                newList.append((re.sub("|".join(self.getContractionList()), "", word[0]), word[1]))
            else:
                newList.append(word)
        return newList

    def removeContractions(self, wordList):
        newList = []
        for word in wordList:
            # if word in self.getContractionList()
            if any(contraction in word for contraction in self.getContractionList()):
                newList.append(re.sub("|".join(self.getContractionList()), "", word))
            else:
                newList.append(word)
        return newList


    def wordFrequency(self, wordList):
        # wordList = self.getWordList(True)
        # lemmaWordList = self.lemmatizeSentence(wordList)
        frequencyList = FreqDist(wordList).most_common(100)
        # frequencyList = {}
        # for word in lemmaWordList:
        #     if word in frequencyList.keys():
        #         frequencyList[word] += 1
        #     else:
        #         frequencyList[word] = 1
        return frequencyList

    def countSyllable(self, wordList):
        hypeneter = pyphen.Pyphen(lang='en')
        noOfSyllable = 0
        for eachWord in wordList:
            noOfSyllable += len(hypeneter.inserted(eachWord).split('-'))
        return noOfSyllable

    def getNumericData(self):
        sentences = sent_tokenize(self.text)
        wordList = self.getWordList(self.text, False)
        # onlyWord = [word[0] for word in wordList]
        uniquWords = set(wordList)
        noOfSentences = len(sentences)
        noOfWords = len(wordList)
        noOfUniqueWords = len(uniquWords)
        noOfCharacters = 0
        longSentence = 0
        # for word in wordList:
        noOfCharacters = len(self.text.strip(" "))

        for sentence in sentences:
            if len(sentence.split()) > 20:
                longSentence += 1

        avgLetters = (noOfCharacters/noOfWords)*100
        avgSentences = (noOfSentences/noOfWords)*100
        noOfSyllable = self.countSyllable(wordList)
        lexicalDiversity = (noOfUniqueWords/noOfWords)*100

        return {
            "noOfWords": noOfWords,
            "noOfSentences": noOfSentences,
            "noOfCharacters": noOfCharacters,
            "avgLetters": avgLetters,
            "avgSentences": avgSentences,
            "noOfSyllable": noOfSyllable,
            "noOfUniqueWords": noOfUniqueWords,
            "lexicalDiversity": lexicalDiversity,
            "longSentence": longSentence
        }


    def complexity(self):
        stats = self.getNumericData()
        ari = 4.71*(stats["noOfCharacters"]/stats["noOfWords"]) + 0.5*(stats["noOfWords"]/stats["noOfSentences"]) - 21.43
        gradeAri = self.ariGrade(ari)
        cli = 0.0588*stats["avgLetters"] - 0.296*stats["avgSentences"] - 15.8
        gradeCli = self.cliGrade(cli)
        fre = 206.835 - 1.015*(stats["noOfWords"]/stats["noOfSentences"]) - 84.6*(stats["noOfSyllable"]/stats["noOfWords"])
        gradeFre = self.freGrade(fre)
        return {
            "ARI": ari,
            "gradeAri": gradeAri,
            "CLI": cli,
            "gradeCli": gradeCli,
            "FRE": fre,
            "gradeFre": gradeFre,
            "stats": stats
        }


    def ariGrade(self, ari):
        roundValue = round(ari)
        if roundValue == 1:
            return "Kindergarten"
        elif roundValue == 2:
            return "1st-2nd"
        elif roundValue >= 14:
            return "Graduate"
        elif roundValue >= 13:
            return "College Student"
        else:
            return str(roundValue) + "th"


    def cliGrade(self, cli):
        cliValue = round(cli)
        if cliValue == 1:
            return "1st"
        elif cliValue == 2:
            return "2nd"
        elif cliValue > 16:
            return "Graduate"
        elif cliValue >= 13:
            return "College Student"
        else:
            return str(cliValue) + "th"

    def freGrade(self, fre):
        if fre >= 90:
            return "5th"
        elif fre >= 80:
            return "6th"
        elif fre >= 70:
            return "7th"
        elif fre >= 60:
            return "8th-9th"
        elif fre >= 50:
            return "10th-12th"
        elif fre >= 30:
            return "College Student"
        else:
            return "Graduate"
