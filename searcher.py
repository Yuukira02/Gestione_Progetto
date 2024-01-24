from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh.qparser.dateparse import DateParserPlugin


def execute_query(query):
    """ALGORITMO CHE DATA UNA QUERY ESEGUE LE RISPOSTE"""
    ix = open_dir("indexdir")
    searcher = ix.searcher()

    # parser = MultifieldParser(["title", "content"], ix.schema)
    parser = QueryParser("content", ix.schema)
    parser.add_plugin(DateParserPlugin())
    query = parser.parse(query)

    # results = searcher.search(query, limit=20) || results = searcher.search(query, limit=None)
    results = searcher.search(query, limit=None)
    return results


# TO-DO: in questo caso l'input è da terminale, più avanti sarà da GUI
query = input("Inserisci ciò che vuoi cercare (default: contenuto) \nSuggerito: 'Allarmante!': ")
results = execute_query(query)

for i in range(0, len(results)):
    print(results[i])
# print(results[i] for i in list(range(0, 10)))
