from whoosh.analysis import LanguageAnalyzer, IntraWordFilter
from whoosh.index import create_in
from whoosh.fields import *
from transformers import pipeline
import os


def custom_analyzer():
    ana = LanguageAnalyzer("it") | IntraWordFilter(splitwords=True, splitnums=True, mergewords=False, mergenums=False)
    return ana


def format_date(date):
    date = date[0:10]

    if date[4] != "-" and date[7] != 0:
        print("Error: not a valid date")
        exit()
    return date


def convert_predicted_sentiment(prediction):
    first_value = int(prediction[0][0].get('label')[0])
    second_value = int(prediction[0][1].get('label')[0])
    if first_value + second_value <= 4:
        return -1
    if first_value + second_value >= 8:
        return 1
    else:
        return 0


def add_docs(doc_writer):
    classifier = pipeline("text-classification", model='nlptown/bert-base-multilingual-uncased-sentiment', top_k=2)

    # let us open every textual file our dataset directory
    if not os.path.exists("notizie"):
        os.mkdir("notizie")
    path = "notizie"

    filelist = os.listdir(path)

    for f in filelist:
        if f.endswith(".txt"):
            try:
                fileobj = open(os.path.join(path, f), "r", encoding="utf8")
            except Exception as e:
                print(e)
                exit()

            title = fileobj.readline().removesuffix('\n')
            url = fileobj.readline().removesuffix('\n')
            date = format_date(fileobj.readline())
            content = fileobj.read().removesuffix('\n')
            prediction = classifier(title)
            sentiment = convert_predicted_sentiment(prediction)
            fileobj.close()

            doc_writer.add_document(title=title, content=content, sentiment=sentiment, url=url, date=date)


# indexing
def create_index():
    schema = Schema(title=TEXT(stored=True, analyzer=custom_analyzer()), content=TEXT(stored=True, analyzer=custom_analyzer()), sentiment=NUMERIC(),
                    url=ID(stored=True), date=DATETIME(stored=True))

    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")

    ix = create_in("indexdir", schema)
    writer = ix.writer()

    add_docs(writer)
    writer.commit()


if __name__=="__main__":
    print("inizio indexing")
    create_index()
    print("index creato")
