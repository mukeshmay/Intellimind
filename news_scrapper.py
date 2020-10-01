import pickle
import sys
import os
import newspaper
from newspaper import news_pool
import pymongo
from datetime import datetime, date, time
import threading 

def news(site, col):
    site_paper = newspaper.build(site, memoize_articles=False)
    dbfile = open('symbols.pickle', 'rb')
    db2 = pickle.load(dbfile)
    print(site, len(site_paper.articles)) 
    
    for article in site_paper.articles:
        try:
            article.download()
            article.parse()
            article.nlp()
            article.keywords = [x.lower() for x in article.keywords]
        except:
            continue

        #print(article.keywords)
        for i in range(len(db2['symbol'])):
            symbol = db2['symbol'][i]
            company = db2['company'][i]
            company = company.lower()
            #print(symbol, company)
            if company in article.keywords:
                
                datetimenow = datetime.now()
                date = datetimenow.replace(hour=0, minute=0, second=0, microsecond=0)
                testobj = {"current_date":date}
                
                mydoc = col.find_one(testobj)
                
                if mydoc==None:
                    obj = {
                        "current_date":date,
                        "article": []
                    }
                    col.insert_one(obj)
                
                articlepost = {
                    "security":symbol,
                    "author": article.authors,
                    "story_date": article.publish_date,
                    "title": article.title,
                    "summary": article.summary,
                    "source": site,
                    "current_datetime": datetimenow
                }

                mydoc = col.find_one(testobj)
                articles = mydoc['article'] 

                unique=1
                for art in articles:
                    if(art['security']==articlepost['security'] and art['author']==articlepost['author'] 
                    and art['title']==articlepost['title'] and art['source']==articlepost['source'] ):
                        unique = 0
                if unique:
                    articles.append(articlepost)
                    newvalues = { "$set": { "article": articles} }
                    col.update_one(testobj, newvalues)


if __name__ == '__main__': 

    client = pymongo.MongoClient("mongodb+srv://Me:blurryface26Muk@cluster0.evtzr.mongodb.net/database0?retryWrites=true&w=majority")
    db = client["database0"]
    col = db["news-article"]

    #os.mkdir(sys.argv[1])

    siteslist = open(sys.argv[2], 'r')
    #outputfile = open(sys.argv[1], 'w')
    sites = siteslist.readlines()
    #for site in sites:
    #    print(site)

    
    #for keys in db: 
    #print(db['symbol'][504])
    site_papers = []
    for site in sites:
        site_papers.append(newspaper.build(site, memoize_articles=False))

    threads=[]
    for site in sites:
        threads.append(threading.Thread(target=news, args=(site,col)))
    
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
    
