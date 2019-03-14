import os
from preprocess import PreProcess
import time

start_time = time.time()
thisTime = start_time
files = []
dataFolder = os.path.dirname(os.path.abspath(__file__)) + "/data"
resultFolder = os.path.dirname(os.path.abspath(__file__)) + "/result"
count = 0
for i in os.listdir(dataFolder):
    if i.endswith('.txt'):
        thisFile = os.path.join(dataFolder, i)
        reflection = open(thisFile, "r", encoding="utf8")

        processData = PreProcess(reflection.read())
        readability = processData.complexity()
        # print(os.path.basename(reflection.name))
        # break
        result = open(resultFolder + "/test_with_stop.csv", "a+")
        if count == 0:
            print("\n\n")
            result.write("FileName,WordCount,UniqeWordCount,LexicalDiversity,SentenceCount,Sentence > 20 Words,SyllableCount,ARI,ARI Grade, CLI,CLI Grade, FRE, FRE Grade\n")
        result.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" %(reflection.name,readability["stats"]['noOfWords'],readability["stats"]['noOfUniqueWords'],str(readability["stats"]["lexicalDiversity"])+"%",readability["stats"]['noOfSentences'],readability["stats"]['longSentence'],readability["stats"]['noOfSyllable'],readability["ARI"],readability["gradeAri"],readability["CLI"],readability["gradeCli"],readability["FRE"],readability["gradeFre"]))

        print("File %s Processed Time: --- %s seconds ---" % (os.path.basename(reflection.name), (time.time() - thisTime)))
        thisTime = time.time()
        result.close()
        reflection.close()

    count += 1

print("\nTotal processed Time: --- %s seconds ---\n\n" % (time.time() - start_time))
