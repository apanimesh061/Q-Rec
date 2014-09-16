#!C:\Python27\python.exe

import stackexchange
import _mysql
import nltk

con = None
try:
    con = _mysql.connect('localhost', 'deadAngel', '', 'test')
except _mysql.Error, e:
    print "Error in connecting to MySql"

so = stackexchange.StackOverflow()
csvfile = "D:\\questions.csv";
fil = open(csvfile, 'w');
count = 0

for q in so.questions(pagesize=100):
    con.ping(1)
    count = count + 1
    topic = q.title.encode('ascii', 'ignore')
    topic = topic.replace(',', '')
    topic = topic.replace("'", '')
    topic = topic.replace('"', '')
    link = q.url
    
    inputt = 'insert into ngrams values (' + '\'' + topic + '\'' + ', ' + '\'' + link + '\'' + ')'

    con.query(inputt)
    if(fil):
        fil.write(topic + ',' + link + ',' + '\n')
    if (count == 10000):
        break

if con:
    con.close()
fil.close()
