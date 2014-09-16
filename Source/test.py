#!C:\Python27\python.exe

import stackexchange
import numpy as np
import numpy.linalg as LA
import MySQLdb
import gensim, re
import nltk

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from nltk.corpus import stopwords
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, wordpunct_tokenize, sent_tokenize
from gensim import corpora, models, similarities
from functools import partial


import cgi, cgitb 
cgitb.enable();
form = cgi.FieldStorage()

SEED = 42
np.random.seed(SEED)

print "Content-Type: text/html\n\n"

if form.getvalue("w"):
   text_content = form.getvalue("w")
else:
   text_content = ""

#text_content = 'How to parse JSON in JavaScript'
#text_content = 'Changelog generation from Github issues?'
#text_content = 'Why ASP.NET MVC doesnt send a response when I call Json(null)'
#text_content = 'Confusion between merge and commit in Git'

max_q = 10

train_set = []
url_set   = []

punctuation_string = ',/;-=+?><":|\/()?~`!@#$%^&*'
stoplist = nltk.corpus.stopwords.words('english')
stopwords_list_II = "way,use,first,second,third,using,one,two,three,four,five,six,seven,eight,nine,ten,next,way,look,wasnt,doesnt,hadnt,didnt,couldnt,using,always,within,required,getting,another,a,as,able,about,above,according,accordingly,across,actually,after,afterwards,again,against,ain,t,all,allow,allows,almost,alone,along,already,also,although,always,am,among,amongst,an,and,another,any,anybody,anyhow,anyone,anything,anyway,anyways,anywhere,apart,appear,appreciate,appropriate,are,aren,t,around,as,aside,ask,asking,associated,at,available,away,awfully,be,became,because,become,becomes,becoming,been,before,beforehand,behind,being,believe,below,beside,besides,best,better,between,beyond,both,brief,but,by,c,mon,c,s,came,can,can,t,cannot,cant,cause,causes,certain,certainly,changes,clearly,co,com,come,comes,concerning,consequently,consider,considering,contain,containing,contains,corresponding,could,couldn,t,course,currently,definitely,described,despite,did,didn,t,different,do,does,doesn,t,doing,don,t,done,down,downwards,during,each,edu,eg,eight,either,else,elsewhere,enough,entirely,especially,et,etc,even,ever,every,everybody,everyone,everything,everywhere,ex,exactly,example,except,far,few,fifth,first,five,followed,following,follows,for,former,formerly,forth,four,from,further,furthermore,get,gets,getting,given,gives,go,goes,going,gone,got,gotten,greetings,had,hadn,t,happens,hardly,has,hasn,t,have,haven,t,having,he,he,s,hello,help,hence,her,here,here,s,hereafter,hereby,herein,hereupon,hers,herself,hi,him,himself,his,hither,hopefully,how,howbeit,however,i,d,i,ll,i,m,i,ve,ie,if,ignored,immediate,in,inasmuch,inc,indeed,indicate,indicated,indicates,inner,insofar,instead,into,inward,is,isn,t,it,it,d,it,ll,it,s,its,itself,just,keep,keeps,kept,know,knows,known,last,lately,later,latter,latterly,least,less,lest,let,let,s,like,liked,likely,little,look,looking,looks,ltd,mainly,many,may,maybe,me,mean,meanwhile,merely,might,more,moreover,most,mostly,much,must,my,myself,name,namely,nd,near,nearly,necessary,need,needs,neither,never,nevertheless,new,next,nine,no,nobody,non,none,noone,nor,normally,not,nothing,novel,now,nowhere,obviously,of,off,often,oh,ok,okay,old,on,once,one,ones,only,onto,or,other,others,otherwise,ought,our,ours,ourselves,out,outside,over,overall,own,particular,particularly,per,perhaps,placed,please,plus,possible,presumably,probably,provides,que,quite,qv,rather,rd,re,really,reasonably,regarding,regardless,regards,relatively,respectively,right,said,same,saw,say,saying,says,second,secondly,see,seeing,seem,seemed,seeming,seems,seen,self,selves,sensible,sent,serious,seriously,seven,several,shall,she,should,shouldn,t,since,six,so,some,somebody,somehow,someone,something,sometime,sometimes,somewhat,somewhere,soon,sorry,specified,specify,specifying,still,sub,such,sup,sure,t,s,take,taken,tell,tends,th,than,thank,thanks,thanx,that,that,s,thats,the,their,theirs,them,themselves,then,thence,there,there,s,thereafter,thereby,therefore,therein,theres,thereupon,these,they,they,d,they,ll,they,re,they,ve,think,third,this,thorough,thoroughly,those,though,three,through,throughout,thru,thus,to,together,too,took,toward,towards,tried,tries,truly,try,trying,twice,two,un,under,unfortunately,unless,unlikely,until,unto,up,upon,us,use,used,useful,uses,using,usually,value,various,very,via,viz,vs,want,wants,was,wasn,t,way,we,we,d,we,ll,we,re,we,ve,welcome,well,went,were,weren,t,what,what,s,whatever,when,whence,whenever,where,where,s,whereafter,whereas,whereby,wherein,whereupon,wherever,whether,which,while,whither,who,who,s,whoever,whole,whom,whose,why,will,willing,wish,with,within,without,won,t,wonder,would,would,wouldn,t,yes,yet,you,you,d,you,ll,you,re,you,ve,your,yours,yourself,yourselves,zero".split(',')
stoplist.append(stopwords_list_II)

##-----------------------------------------------------------##
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

    word_count_array = np.empty((len(topic_vec), 2), dtype = np.object)
    for i in range(len(topic_vec)):
        word_count_array[i, 0] = topic_vec[i][0]
        word_count_array[i, 1] = topic_vec[i][1]

    idx = np.argsort(word_count_array[:, 1])
    idx = idx[::-1]
    word_count_array = word_count_array[idx]

    final = []
    final = lda.print_topic(word_count_array[0, 0], 5)

    final = final.split('+')
    temp_final = []
    for f in final:
       temp_final.append(f.lstrip(' ').rstrip(' ').split('*'))
   
    final = [temp_final[i][1] for i in range(len(temp_final))]
    del(temp_final)
    final = [t[0].upper() + t[1:] for t in final]
    #final = ' '.join(final)

    return final

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

##-----------------------------------------------------------##
con = None
try:
    con = MySQLdb.connect('localhost', 'deadAngel', '', 'test')
except MySQLdb.Error, e:
    print "Error in connecting to MySql"

cur = con.cursor()
cur.execute("Select * from questions limit 0,4000")
data = cur.fetchall()

for row in data:
    train_set.append(row[0])
    url_set.append(row[1])

cur.close()

con.close()
##-----------------------------------------------------------##

lda_model = [gensim.models.ldamodel.LdaModel.load('lda50_questions.model'),
        gensim.models.ldamodel.LdaModel.load('lda40_questions.model'),
        gensim.models.ldamodel.LdaModel.load('lda30_questions.model'),
        gensim.models.ldamodel.LdaModel.load('lda20_questions.model'),
        gensim.models.ldamodel.LdaModel.load('lda10_questions.model')]
lda = lda_model[0]
qlist = []
qlist = lda.show_topics(50)
topic_list = []
topic_list = getTopicList(qlist)

topic_of_query = getTopicForQuery(text_content)

count         = 0
question_list = []
cosine_list   = []
count_list    = []
url_list      = []

## Changelog generation from Github issues? How to parse JSON in JavaScript

test_set  = [text_content]
stopWords = stopwords.words('english')

vectorizer  = CountVectorizer(stop_words = stopWords, min_df=1)
transformer = TfidfTransformer()

trainVectorizerArray = vectorizer.fit_transform(train_set).toarray()
testVectorizerArray  = vectorizer.transform(test_set).toarray()

cx = lambda a, b : round(np.inner(a, b)/(LA.norm(a)*LA.norm(b)), 6)

for vector in trainVectorizerArray:
    count = count + 1
    for testV in testVectorizerArray:
        if (sum(testV) > 0):
            cosine = cx(vector, testV)
            if (cosine > 0.0):
                #print count, cosine, train_set[count-1], url_set[count-1]
                count_list.append(count)
                cosine_list.append(cosine)
                question_list.append(train_set[count-1])
                url_list.append(url_set[count-1])

count_list    = np.array(count_list)
cosine_list   = np.array(cosine_list)
question_list = np.array(question_list)
url_list      = np.array(url_list)

index         = cosine_list.argsort()
index         = index[::-1]
question_list = question_list[index]
url_list      = url_list[index]

topic     = []
ques_list = []

topic, ques_list = retrieveClusters()

print '<h2>These Queries seem to similar to that posted... :</h2>'
print '<ol>'
for url, q in zip(url_list[0 : max_q], question_list[0 : max_q]):
	print r'<li><a href="{0}">{1}</a></li><br>'.format(url, q)
print '</ol>'

#print r'<p style="font-size:16pt;font-color:green;">{0}</p>'.format(topic_of_query)
print '<br><br>'
print '<h2>Following are the possible tags for the query:</h2>'

print '<div class="buttons" style="padding-bottom:40px;">'
for f in topic_of_query:
   print r'<a href="#" class="button big">{0}</a>'.format(f)
print '</div>'

print '<br><br><br>'

print '<h2>The 50 clusters from the trained model are:</h2>'
print """<div style="font-size:12pt;font-weight:bold;" class="dropt">"""

for i in range(len(topic)):
   #print r'[{0}] cluster contains {1} Documents<br>'.format(topic[i][0].upper() + topic[i][1:], len(ques_list[i]))
   print r'<a href="#" class="button info">{0}<span class="ttip">{1} Documents</span></a>&nbsp&nbsp'.format(topic[i][0].upper() + topic[i][1:], len(ques_list[i]))
	
print """</div>"""
