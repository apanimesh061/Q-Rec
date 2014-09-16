#!C:\Python27\python.exe

import nltk, gensim
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, wordpunct_tokenize, sent_tokenize
from gensim import corpora, models, similarities
import MySQLdb

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

documents = []
punctuation_string = ',/;-=+?><":|\/()?~`!@#$%^&*'
stoplist = nltk.corpus.stopwords.words('english')
stopwords_list_II = "send,ignore,number,class,change,creating,server,external,values,method,page,line,test,loop,file,time,images,way,use,first,second,third,using,one,two,three,four,five,six,seven,eight,nine,ten,next,way,look,wasnt,doesnt,hadnt,didnt,couldnt,using,always,within,required,getting,another,a,as,able,about,above,according,accordingly,across,actually,after,afterwards,again,against,ain,t,all,allow,allows,almost,alone,along,already,also,although,always,am,among,amongst,an,and,another,any,anybody,anyhow,anyone,anything,anyway,anyways,anywhere,apart,appear,appreciate,appropriate,are,aren,t,around,as,aside,ask,asking,associated,at,available,away,awfully,be,became,because,become,becomes,becoming,been,before,beforehand,behind,being,believe,below,beside,besides,best,better,between,beyond,both,brief,but,by,c,mon,c,s,came,can,can,t,cannot,cant,cause,causes,certain,certainly,changes,clearly,co,com,come,comes,concerning,consequently,consider,considering,contain,containing,contains,corresponding,could,couldn,t,course,currently,definitely,described,despite,did,didn,t,different,do,does,doesn,t,doing,don,t,done,down,downwards,during,each,edu,eg,eight,either,else,elsewhere,enough,entirely,especially,et,etc,even,ever,every,everybody,everyone,everything,everywhere,ex,exactly,example,except,far,few,fifth,first,five,followed,following,follows,for,former,formerly,forth,four,from,further,furthermore,get,gets,getting,given,gives,go,goes,going,gone,got,gotten,greetings,had,hadn,t,happens,hardly,has,hasn,t,have,haven,t,having,he,he,s,hello,help,hence,her,here,here,s,hereafter,hereby,herein,hereupon,hers,herself,hi,him,himself,his,hither,hopefully,how,howbeit,however,i,d,i,ll,i,m,i,ve,ie,if,ignored,immediate,in,inasmuch,inc,indeed,indicate,indicated,indicates,inner,insofar,instead,into,inward,is,isn,t,it,it,d,it,ll,it,s,its,itself,just,keep,keeps,kept,know,knows,known,last,lately,later,latter,latterly,least,less,lest,let,let,s,like,liked,likely,little,look,looking,looks,ltd,mainly,many,may,maybe,me,mean,meanwhile,merely,might,more,moreover,most,mostly,much,must,my,myself,name,namely,nd,near,nearly,necessary,need,needs,neither,never,nevertheless,new,next,nine,no,nobody,non,none,noone,nor,normally,not,nothing,novel,now,nowhere,obviously,of,off,often,oh,ok,okay,old,on,once,one,ones,only,onto,or,other,others,otherwise,ought,our,ours,ourselves,out,outside,over,overall,own,particular,particularly,per,perhaps,placed,please,plus,possible,presumably,probably,provides,que,quite,qv,rather,rd,re,really,reasonably,regarding,regardless,regards,relatively,respectively,right,said,same,saw,say,saying,says,second,secondly,see,seeing,seem,seemed,seeming,seems,seen,self,selves,sensible,sent,serious,seriously,seven,several,shall,she,should,shouldn,t,since,six,so,some,somebody,somehow,someone,something,sometime,sometimes,somewhat,somewhere,soon,sorry,specified,specify,specifying,still,sub,such,sup,sure,t,s,take,taken,tell,tends,th,than,thank,thanks,thanx,that,that,s,thats,the,their,theirs,them,themselves,then,thence,there,there,s,thereafter,thereby,therefore,therein,theres,thereupon,these,they,they,d,they,ll,they,re,they,ve,think,third,this,thorough,thoroughly,those,though,three,through,throughout,thru,thus,to,together,too,took,toward,towards,tried,tries,truly,try,trying,twice,two,un,under,unfortunately,unless,unlikely,until,unto,up,upon,us,use,used,useful,uses,using,usually,value,various,very,via,viz,vs,want,wants,was,wasn,t,way,we,we,d,we,ll,we,re,we,ve,welcome,well,went,were,weren,t,what,what,s,whatever,when,whence,whenever,where,where,s,whereafter,whereas,whereby,wherein,whereupon,wherever,whether,which,while,whither,who,who,s,whoever,whole,whom,whose,why,will,willing,wish,with,within,without,won,t,wonder,would,would,wouldn,t,yes,yet,you,you,d,you,ll,you,re,you,ve,your,yours,yourself,yourselves,zero".split(',')
stoplist = stoplist + stopwords_list_II

con = None
try:
    con = MySQLdb.connect('localhost', 'deadAngel', '', 'test')
except MySQLdb.Error, e:
    print "Error in connecting to MySql"

cur = con.cursor()
cur.execute("Select title from questions")
data = cur.fetchall()

for row in data:
    temp = row[0]
    for i in range(len(punctuation_string)):
        temp = temp.replace(punctuation_string[i], '')
    documents.append(temp.lower())

cur.close()
con.close()

texts = [[word for word in document.lower().split() if word not in stoplist]for document in documents]

final_text = []

for i in range(len(texts)):
    final_text.append(filter(lambda word: word not in punctuation_string, set(texts[i])))

final_filtered_text = []
final_filtered_text = [[word for word in text if word not in stoplist] for text in texts]

dictionary = corpora.Dictionary(final_filtered_text)
dictionary.save('questions.dict');

corpus = [dictionary.doc2bow(text) for text in final_filtered_text]

corpora.MmCorpus.serialize      ('questions.mm'      , corpus)
corpora.SvmLightCorpus.serialize('questions.svmlight', corpus)
corpora.BleiCorpus.serialize    ('questions.lda-c'   , corpus)
corpora.LowCorpus.serialize     ('questions.low'     , corpus)

mm = corpora.MmCorpus('questions.mm')

lda5 = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=dictionary, num_topics=50, update_every=0, chunksize=19188, passes=200)
lda5.save('lda50_questions.model')

lda4 = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=dictionary, num_topics=40, update_every=0, chunksize=19188, passes=200)
lda4.save('lda40_questions.model')

lda3 = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=dictionary, num_topics=30, update_every=0, chunksize=19188, passes=200)
lda3.save('lda30_questions.model')

lda2 = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=dictionary, num_topics=20, update_every=0, chunksize=19188, passes=200)
lda2.save('lda20_questions.model')

lda1 = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=dictionary, num_topics=10, update_every=0, chunksize=19188, passes=200)
lda1.save('lda10_questions.model')
