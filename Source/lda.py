#!C:\Python27\python.exe

import gensim, re, MySQLdb
import nltk, numpy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, wordpunct_tokenize, sent_tokenize
from gensim import corpora, models, similarities
from functools import partial

punctuation_string = ',/;-=+?><":|\/()?~`!@#$%^&*'
stoplist = nltk.corpus.stopwords.words('english')
stopwords_list_II = "send,ignore,number,class,change,creating,server,external,values,method,page,line,test,loop,file,time,images,way,use,first,second,third,using,one,two,three,four,five,six,seven,eight,nine,ten,next,way,look,wasnt,doesnt,hadnt,didnt,couldnt,using,always,within,required,getting,another,a,as,able,about,above,according,accordingly,across,actually,after,afterwards,again,against,ain,t,all,allow,allows,almost,alone,along,already,also,although,always,am,among,amongst,an,and,another,any,anybody,anyhow,anyone,anything,anyway,anyways,anywhere,apart,appear,appreciate,appropriate,are,aren,t,around,as,aside,ask,asking,associated,at,available,away,awfully,be,became,because,become,becomes,becoming,been,before,beforehand,behind,being,believe,below,beside,besides,best,better,between,beyond,both,brief,but,by,c,mon,c,s,came,can,can,t,cannot,cant,cause,causes,certain,certainly,changes,clearly,co,com,come,comes,concerning,consequently,consider,considering,contain,containing,contains,corresponding,could,couldn,t,course,currently,definitely,described,despite,did,didn,t,different,do,does,doesn,t,doing,don,t,done,down,downwards,during,each,edu,eg,eight,either,else,elsewhere,enough,entirely,especially,et,etc,even,ever,every,everybody,everyone,everything,everywhere,ex,exactly,example,except,far,few,fifth,first,five,followed,following,follows,for,former,formerly,forth,four,from,further,furthermore,get,gets,getting,given,gives,go,goes,going,gone,got,gotten,greetings,had,hadn,t,happens,hardly,has,hasn,t,have,haven,t,having,he,he,s,hello,help,hence,her,here,here,s,hereafter,hereby,herein,hereupon,hers,herself,hi,him,himself,his,hither,hopefully,how,howbeit,however,i,d,i,ll,i,m,i,ve,ie,if,ignored,immediate,in,inasmuch,inc,indeed,indicate,indicated,indicates,inner,insofar,instead,into,inward,is,isn,t,it,it,d,it,ll,it,s,its,itself,just,keep,keeps,kept,know,knows,known,last,lately,later,latter,latterly,least,less,lest,let,let,s,like,liked,likely,little,look,looking,looks,ltd,mainly,many,may,maybe,me,mean,meanwhile,merely,might,more,moreover,most,mostly,much,must,my,myself,name,namely,nd,near,nearly,necessary,need,needs,neither,never,nevertheless,new,next,nine,no,nobody,non,none,noone,nor,normally,not,nothing,novel,now,nowhere,obviously,of,off,often,oh,ok,okay,old,on,once,one,ones,only,onto,or,other,others,otherwise,ought,our,ours,ourselves,out,outside,over,overall,own,particular,particularly,per,perhaps,placed,please,plus,possible,presumably,probably,provides,que,quite,qv,rather,rd,re,really,reasonably,regarding,regardless,regards,relatively,respectively,right,said,same,saw,say,saying,says,second,secondly,see,seeing,seem,seemed,seeming,seems,seen,self,selves,sensible,sent,serious,seriously,seven,several,shall,she,should,shouldn,t,since,six,so,some,somebody,somehow,someone,something,sometime,sometimes,somewhat,somewhere,soon,sorry,specified,specify,specifying,still,sub,such,sup,sure,t,s,take,taken,tell,tends,th,than,thank,thanks,thanx,that,that,s,thats,the,their,theirs,them,themselves,then,thence,there,there,s,thereafter,thereby,therefore,therein,theres,thereupon,these,they,they,d,they,ll,they,re,they,ve,think,third,this,thorough,thoroughly,those,though,three,through,throughout,thru,thus,to,together,too,took,toward,towards,tried,tries,truly,try,trying,twice,two,un,under,unfortunately,unless,unlikely,until,unto,up,upon,us,use,used,useful,uses,using,usually,value,various,very,via,viz,vs,want,wants,was,wasn,t,way,we,we,d,we,ll,we,re,we,ve,welcome,well,went,were,weren,t,what,what,s,whatever,when,whence,whenever,where,where,s,whereafter,whereas,whereby,wherein,whereupon,wherever,whether,which,while,whither,who,who,s,whoever,whole,whom,whose,why,will,willing,wish,with,within,without,won,t,wonder,would,would,wouldn,t,yes,yet,you,you,d,you,ll,you,re,you,ve,your,yours,yourself,yourselves,zero".split(',')
stoplist.append(stopwords_list_II)

def getTopicList (full_list):
    temp_list  = []
    topic_list = []
    for i in range(len(full_list)):
        temp_list.append(full_list[i].replace(' ','').split('+'))
    for i in range(len(temp_list)):
        temp_split = temp_list[i][0].split('*')
        topic_list.append(temp_split[1])
    return topic_list

def getTopicForQuery (question):
    temp = question.lower()
    for i in range(len(punctuation_string)):
        temp = temp.replace(punctuation_string[i], '')

    words = re.findall(r'\w+', temp, flags = re.UNICODE | re.LOCALE)

    important_words = []
    important_words = filter(lambda x: x not in stoplist, words)

    dictionary = corpora.Dictionary.load('questions.dict')

    ques_vec = []
    ques_vec = dictionary.doc2bow(important_words)

    topic_vec = []
    topic_vec = lda[ques_vec]

    word_count_array = numpy.empty((len(topic_vec), 2), dtype = numpy.object)
    for i in range(len(topic_vec)):
        word_count_array[i, 0] = topic_vec[i][0]
        word_count_array[i, 1] = topic_vec[i][1]

    idx = numpy.argsort(word_count_array[:, 1])
    idx = idx[::-1]
    word_count_array = word_count_array[idx]

    final = []
    final = lda.print_topic(word_count_array[0, 0], 1)

    question_topic = final.split('*')

    return question_topic[1]

def retrieveDocs():
    original_docs = []
    documents = []
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
        temp = row[0]
        for i in range(len(punctuation_string)):
            temp = temp.replace(punctuation_string[i], '')
        documents.append(temp.lower())

    cur.close()
    con.close()

    return documents, original_docs

def list_duplicates_of (seq, item):
    start_at = -1
    locs = []
    while True:
        try:
            loc = seq.index(item, start_at + 1)
        except ValueError:
            break
        else:
            locs.append(loc)
            start_at = loc
    return locs

def insertValuesToDB (c, list_questions):
    con = None
    try:
        con = MySQLdb.connect('localhost', 'deadAngel', '', 'test')
    except MySQLdb.Error, e:
        print "Error in connecting to MySql"

    cur = con.cursor()
    add_data = ("insert into `cluster_questions` "
                "(`topic`, `index`) "
                "values (%s, %s)")

    print len(c)
    for i in range(len(c)):
        temp = (c[i], list_questions[i])
        cur.execute(add_data, temp)
        con.commit()

    cur.close()
    con.close()

    print "Cluster database updated!"

##-------------------------------------------------------------------------

print "Began!"

original_docs = []
documents = []
documents, original_docs = retrieveDocs()
print "Database query completed!"

lda = [gensim.models.ldamodel.LdaModel.load('lda50_questions.model'),
        gensim.models.ldamodel.LdaModel.load('lda40_questions.model'),
        gensim.models.ldamodel.LdaModel.load('lda30_questions.model'),
        gensim.models.ldamodel.LdaModel.load('lda20_questions.model'),
        gensim.models.ldamodel.LdaModel.load('lda10_questions.model')]

print "Lda Model loaded and topics retrieved!\n"

max_topics = 50

for i in range(len(lda)):
    qlist = []
    qlist = lda[i].show_topics(max_topics - i*10)
    topic_list = []
    topic_list = getTopicList(qlist)
    print topic_list
    del qlist[:]

topics_for_db = []
for i in range(len(documents)):
    topics_for_db.append(getTopicForQuery(documents[i]))

dups_in_source = partial(list_duplicates_of, topics_for_db)

list_questions = []

for c in topic_list:
    questions_cluster = []
    for i in dups_in_source(c):
        questions_cluster.append(original_docs[i])
    #print c, questions_cluster
    temp_list_questions = ','.join(str(e) for e in dups_in_source(c))
    if (len(temp_list_questions) == 0):
        temp_list_questions = 'NULL'
    list_questions.append(temp_list_questions)
    #print c, temp_list_questions

insertValuesToDB (topic_list, list_questions)

print "\nDone!"
