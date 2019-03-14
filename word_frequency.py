import os
from preprocess import PreProcess
import time

start_time = time.time()
thisTime = start_time
files = []
dataFolder = os.path.dirname(os.path.abspath(__file__)) + "/data"
resultFolder = os.path.dirname(os.path.abspath(__file__)) + "/result"
count = 0
commonWordList = {}
for i in os.listdir(dataFolder):
    if i.endswith('.txt'):
        thisFile = os.path.join(dataFolder, i)
        reflection = open(thisFile, "r", encoding="utf8")

        processData = PreProcess(reflection.read())
        wordList = processData.getWordList(reflection.read(), True)
        wordFrequency = processData.wordFrequency(wordList)


        for wordTuple in wordFrequency:
            commonWordList[wordTuple[0]] = commonWordList[wordTuple[0]] + wordTuple[1] if wordTuple[0] in commonWordList else wordTuple[1]

        print("--- %s seconds ---" % (time.time() - thisTime))
        thisTime = time.time()


        reflection.close()

result = open(resultFolder + "/wordfrequency.csv", "a+")
result.write("Word,WordCount\n")
iter = 0
for key,value in sorted(commonWordList.items(), key=lambda x: x[1], reverse=True):
    if iter == 100:
        break
    result.write("%s,%s\n" %(key,value))
    iter += 1

print("Total Time --- %s seconds ---" % (time.time() - start_time))

result.close()
