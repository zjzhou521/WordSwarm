import datetime
import string
import nltk
import os

nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import math
import pandas as pd
import time


def print_docs(text):
    for line in text:
        print(line)
    print("--------------------------------")


def print_matrix_int(m):  # dict{key, list}
    for key in m.keys():
        print(key.ljust(20), end="")
        print(m[key])
    print("--------------------------------")


def print_matrix_float(m):  # dict{key, list}
    for key in m.keys():
        print(key.ljust(12), end="")
        for num in m[key]:
            print("%.2f" % num, end=" ")
        print()
    print("--------------------------------")


def remove_punctuation(doc):
    punctuation_chars = string.punctuation  # reference: https://blog.csdn.net/weixin_38819889/article/details/105389248
    for c in punctuation_chars:
        doc = doc.replace(c, '')
    return doc


def remove_stopwords(doc):
    stop_words = set(
        stopwords.words('english'))  # reference: https://iowiki.com/python_text/python_remove_stopwords.html
    docWordArray = doc.split(" ")
    newDoc = ""
    for j in range(len(docWordArray)):
        word = docWordArray[j]
        if word in stop_words:
            continue
        else:
            if j == len(docWordArray) - 1:
                newDoc += word
            else:
                newDoc += word + " "
    return newDoc


def lemmatization(doc):
    lemmatizer = WordNetLemmatizer()  # reference: https://www.imangodoc.com/668.html
    docWordArray = doc.split(" ")
    newDoc = ""
    for j in range(len(docWordArray)):
        word = docWordArray[j]
        word = lemmatizer.lemmatize(word)
        if j == len(docWordArray) - 1:
            newDoc += word
        else:
            newDoc += word + " "
    return newDoc


def stemming(doc):
    ps = PorterStemmer()  # reference: https://www.geeksforgeeks.org/python-stemming-words-with-nltk/
    words = word_tokenize(doc)
    newDoc = ""
    for j in range(len(words)):
        word = words[j]
        word = ps.stem(word)
        if j == len(words) - 1:
            newDoc += word
        else:
            newDoc += word + " "
    return newDoc


def preprocessing(docs):
    # print("####### preprocessing #######")
    # print("before:  ")
    # print_docs(docs)
    docs_term_sequence = []
    for doc in docs:
        doc = remove_punctuation(doc)  # remove punctuation
        doc = remove_stopwords(doc)  # remove stop words
        doc = doc.casefold()  # case folding
        doc = lemmatization(doc)  # lemmatization
        doc = stemming(doc)  # stemming
        docs_term_sequence.append(doc.split(" "))
    # print("after:  ")
    # print_docs(docs_term_sequence)
    # print("\n")
    return docs_term_sequence

def get_term_list(docs_term_sequence):
    all_terms = []
    for doc_terms in docs_term_sequence:
        for term in doc_terms:
            if term not in all_terms:
                all_terms.append(term)
    all_terms.sort()
    return all_terms

def get_term_document_matrix(docs_term_sequence):
    # print("####### term-document incidence matrix #######")
    # print("before:  ")
    # print_docs(docs_term_sequence)
    # get all terms
    all_terms = get_term_list(docs_term_sequence)
    # get frequency each doc
    docs_frequency = []
    for doc_terms in docs_term_sequence:
        doc_dir = {}
        for term in all_terms:
            doc_dir[term] = 0
        for term in doc_terms:
            doc_dir[term] += 1
        docs_frequency.append(doc_dir)
    # get term-doc matrix
    term_doc_matrix = {}  # term, doc freq list
    for term in all_terms:
        doc_freq_list = []
        totalFreq = 0
        for i in range(len(docs_frequency)):
            totalFreq += docs_frequency[i][term]
        term_doc_matrix[term] = totalFreq
    # print("after:  ")
    # print_matrix_int(term_doc_matrix)
    # print("\n")
    return term_doc_matrix

def readData():
    tweets = []
    totalDocs = []
    keyword_tweets = {} # term, docList
    keywords = []
    attributes = ["Keywords", "TweetID", "AuthorID", "Hashtags", "Tweet Created at", "Tweet Text", "Likes", "Reply",
                  "Retweets", "Polarity"]
    for k in range(6):
        data = pd.read_csv("../TwitterData/combined_" + str(k + 1) + ".csv")
        for i in range(len(data)):
            curTweet = []
            for j in range(len(attributes)):
                curTweet.append(data[attributes[j]][i])
            tweets.append(curTweet)
            doc = curTweet[5]
            totalDocs.append(doc)
            keyword = str(curTweet[0])
            keyword = keyword[1:]
            if keyword not in keywords:
                keywords.append(keyword)
                keyword_tweets[keyword] = []
            keyword_tweets[keyword].append(curTweet)
    for key in keyword_tweets.keys():
        keyword_tweets[key].sort(key=lambda x: x[4])  # each keyword's tweets based on time
    tweets.sort(key=lambda x: x[4])  # sort based on time
    return tweets, totalDocs, keyword_tweets
def getWordTimeList():
    wordTimeList = []
    timeList = ["2022-01-27 22:30:00", "2022-02-23 04:00:00"]
    startTime = time.strptime(timeList[0], "%Y-%m-%d %H:%M:%S")
    startTime = datetime.datetime(startTime[0], startTime[1], startTime[2], startTime[3], startTime[4], startTime[5])
    endTime = time.strptime(timeList[1], "%Y-%m-%d %H:%M:%S")
    endTime = datetime.datetime(endTime[0], endTime[1], endTime[2], endTime[3], endTime[4], endTime[5])
    curTime = startTime
    cnt = 0
    while curTime < endTime:
        cnt += 1
        # need tweets from [index, curTime)
        curTime += datetime.timedelta(minutes=30)
        wordTimeList.append(curTime)
    return wordTimeList
def createKeywordCSV(keywords):
    os.system("rm timeData/*")
    for keyword in keywords:
        filename = "./timeData/" + keyword + ".csv"
        tmp = []
        dataframe = pd.DataFrame()
        for wtime in wordTimeList:
            dataframe[wtime] = 0
        dataframe.to_csv(filename, index=False, sep=',')

# read in data
tweets, totalDocs, keyword_tweets = readData()
lenTweets = len(tweets)
# print(lenTweets)  # 110900
# print(len(keyword_tweets))  # 29

# generate wordTimeList
wordTimeList = getWordTimeList()  # len = 1259
lenTweets = len(tweets)
index = 0
cnt = 0
os.system("rm ./txtData/*")
for curTime in wordTimeList:
    cnt += 1
    # need tweets from [index, curTime)
    print(str(index) + "/" + str(lenTweets))
    # get docs
    timeDocs = ""
    while index < lenTweets:
        tweetTime = time.strptime(tweets[index][4][:19], "%Y-%m-%d %H:%M:%S")
        tweetTime = datetime.datetime(tweetTime[0], tweetTime[1], tweetTime[2], tweetTime[3], tweetTime[4],
                                      tweetTime[5])
        if tweetTime >= curTime: break
        timeDocs += tweets[index][5] + "\n"  # add tweet text into timeDocs
        index += 1
    filename = "./txtData/" + str(cnt) + ".txt"
    if (timeDocs != ""):
        with open(filename, "w") as file:
            file.write(timeDocs)

