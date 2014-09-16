#!C:\Python27\python.exe

import MySQLdb, numpy

def retrieveClusters():
    topic = []
    ques_list = []
    con = None
    try:
        con = MySQLdb.connect('localhost', 'deadAngel', '', 'test')
    except MySQLdb.Error, e:
        print "Error in connecting to MySql"

    cur = con.cursor()
    cur.execute("Select * from cluster_questions")
    data = cur.fetchall()

    for row in data:
        topic.append(row[0])
        ques_list.append(row[1])

    cur.close()
    con.close()

    return topic, ques_list

def retrieveDocs():
    original_docs = []
    con = None
    try:
        con = MySQLdb.connect('localhost', 'deadAngel', '', 'test')
    except MySQLdb.Error, e:
        print "Error in connecting to MySql"

    cur = con.cursor()
    cur.execute("Select title from questions")
    data = cur.fetchall()

    for row in data:
        original_docs.append(row[0])

    cur.close()
    con.close()

    return original_docs

def showClusters(topic):
    list_ques = []
    con = None
    try:
        con = MySQLdb.connect('localhost', 'deadAngel', '', 'test')
    except MySQLdb.Error, e:
        print "Error in connecting to MySql"

    temp = '%' + topic
    cur = con.cursor()
    cur.execute("select * from cluster_questions where topic like " + "'" + temp + "'")
    data = cur.fetchall()

    for row in data:
        list_ques = row[1]

    cur.close()
    con.close()

    return list_ques

##------------------------------------------------------------------------

topic     = []
ques_list = []
original_docs = []

topic, ques_list = retrieveClusters()
original_docs = retrieveDocs()

questions_cluster = []

for t in topic:
    index_list = showClusters(t).split(',')
    for i in index_list:
        questions_cluster.append(original_docs[i])
    print t, len(index_list)
