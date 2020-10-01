from flask import Flask, request
import pymongo
import datetime
app = Flask(__name__)

@app.route("/")
def home():
    return "Home page"

@app.route("/datetimeapi", methods=["POST"])
def datetimeapi():
    client = pymongo.MongoClient("mongodb+srv://Me:blurryface26Muk@cluster0.evtzr.mongodb.net/database0?retryWrites=true&w=majority")
    db = client["database0"]
    col = db["news-article"]

    input = request.get_json(force=True)
    startdatetime = convert(input["startdatetime"])
    enddatetime = convert(input["enddatetime"])
    startdate = startdatetime.replace(hour=0, minute=0, second=0, microsecond=0)
    enddate = enddatetime.replace(hour=0, minute=0, second=0, microsecond=0)
    myquery = {"current_date":{"$gte":startdate, "$lte":enddate}}

    date_articles = col.find(myquery)
    if date_articles.count()!=0 :
        for date_article in date_articles:
            print(date_article)
            articles=date_article['article']
            articles = [article for article in articles if article['source']==input['source'] and article['current_datetime']>=startdatetime and article['current_datetime']<=enddatetime]
            return {"number_of_articles": len(articles),
            "articles": articles}
    else:
        return {
        "articles": [],
        "number_of_articles": 0
    }
    #return {"date-articles": date_articles.count()}

@app.route("/date", methods=["POST"])
def date():
    client = pymongo.MongoClient("mongodb+srv://Me:blurryface26Muk@cluster0.evtzr.mongodb.net/database0?retryWrites=true&w=majority")
    db = client["database0"]
    col = db["news-article"]

    input = request.get_json(force=True)
    inputdate = convert(input["date"])
    date_articles = col.find_one({"current_date": inputdate})
    if date_articles!=None:
        articles=date_articles['article']
        articles = [article for article in articles if article['source']==input['source']]
        return {"number_of_articles": len(articles),
        "articles": articles}
    else:
        return {
            "articles": [],
            "number_of_articles": 0
        }


def convert(date_time): 
    format = '%b %d %Y %I:%M%p' # The format 
    datetime_str = datetime.datetime.strptime(date_time, format) 
    return datetime_str 


if __name__ == '__main__':
    app.run(debug=True)