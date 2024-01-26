from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh.qparser.dateparse import DateParserPlugin
from transformers import pipeline

classifier = pipeline("text-classification", model='nlptown/bert-base-multilingual-uncased-sentiment', top_k=2)


def convert_predicted_sentiment(prediction):
    print(prediction)
    first_value = int(prediction[0][0].get('label')[0])
    second_value = int(prediction[0][1].get('label')[0])
    if first_value + second_value == 3:
        return -1
    if first_value + second_value == 9:
        return 1
    else:
        return 0


def execute_query(query):
    """ALGORITMO CHE DATA UNA QUERY ESEGUE LE RISPOSTE"""
    ix = open_dir("indexdir")
    searcher = ix.searcher()

    # parser = MultifieldParser(["title", "content"], ix.schema)
    if "sentiment" not in query:
        # valuta la sentiment di una query per aumentare la capacità espressiva
        prediction = classifier(query)
        sentiment = convert_predicted_sentiment(prediction)

        if sentiment == 1:
            query += " AND (sentiment:1 OR sentiment:0)"
        if sentiment == -1:
            query += " AND (sentiment:-1 OR sentiment:0)"
        print(query)
    parser = QueryParser("content", ix.schema)
    parser.add_plugin(DateParserPlugin())
    query = parser.parse(query)

    # results = searcher.search(query, limit=20) || results = searcher.search(query, limit=None)
    results = searcher.search(query, limit=20)
    return results


# TO-DO: in questo caso l'input è da terminale, più avanti sarà da GUI
query = input("Inserisci ciò che vuoi cercare (default: contenuto) \nSuggerito: 'Allarmante!': ")
results = execute_query(query)

for i in range(0, results.scored_length()):
    print(results[i])
