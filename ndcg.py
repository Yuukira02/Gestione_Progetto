from whoosh.index import open_dir
from whoosh.qparser.dateparse import DateParserPlugin
from whoosh.qparser import QueryParser

from sklearn.metrics import ndcg_score
import numpy as np

# VARIABILI GLOBALI NECESSARIE. Ad un utilizzo più ampio, renderemo la lettura del file benchmark.txt più scalato
# VANE: ho utilizzato un benchmark.txt che aveva valori NUM_QUERY = 2 e NUM_R_DOCS = 20
# FATI: avrà un benchmark iniziale con 7 query (base) e 10 risultati per query.
NUM_QUERY = 7
NUM_R_DOCS = 10


# TO-DO: from searcher import execute_query
def execute_query(query):
    """ALGORITMO CHE DATA UNA QUERY ESEGUE LE RISPOSTE"""
    ix = open_dir("indexdir")
    searcher = ix.searcher()

    parser = QueryParser("content", ix.schema)
    parser.add_plugin(DateParserPlugin())
    query = parser.parse(query)

    results = searcher.search(query, limit=None)
    return results


# ALGORITMO CHE LEGGE LA CLASSE BENCHMARK[15 query[20 url]]
# nota: la benchmark è una LISTA di DIZIONARI (query) che associano url (chiavi) a un valore di rilevanza arbitrario.
def read_benchmark():
    path = "benchmark.txt"
    user_query = []
    benchmark = []
    try:
        fileobj = open(path, 'r')
    except Exception as e:
        print(e)
        exit()

    for e in range(NUM_QUERY):
        query = fileobj.readline().removesuffix('\n')
        ideal_answers = {}
        for i in range(NUM_R_DOCS):
            relevance = int(fileobj.read(1))
            # per scartare spazio metasimbolico e non rilevante:
            fileobj.read(1)
            url = fileobj.readline().removesuffix('\n')
            ideal_answers[url] = relevance

        benchmark.append(ideal_answers)
        # per scartare righe con significato metasimbolico e non rilevante
        fileobj.readline()
        user_query.append(query)

    fileobj.close()
    return user_query, benchmark


# ALGORITMO CHE DATE LE RISPOSTE urls[10] ad UNA query, compara le risposte con il benchmark ed assegna un valore
def init_scores(results, benchmark):
    scores = {}
    urls = []
    for i in range(len(results)):
        # equivale a results[i].get('url'), ossia accedere ad una lista di dizionari.
        urls[i] = [results[i]['url']]

    # len(urls) = NUM_DOCS
    for e in range(len(urls)):
        if urls[e] in benchmark[0].keys():
            scores[urls[e]] = benchmark[0].get[urls[e]]
        else:
            scores[urls[e]] = 0
    return scores


def main():
    query, benchmark = read_benchmark()
    media = 0

    # per ogni query in benchmark (tot= NUM_QUERY) , esegue la ndcg.
    for i in range(len(benchmark)):

        # estrai i risultati per la query i di 7 (=NUM_QUERY)
        results = execute_query(query[i])
        scores = init_scores(results, benchmark)

        # estraggo i valori (url, val) dalla query i-esima dal benchmark
        true_relevance = benchmark[i]
        # poi ne estraggo semplicemente la lista di valori ideali per confrontarlo con i valori reali
        # NOTA: effettuiamo conversione con numpy
        true_relevance = np.asarray([list(true_relevance.values())])
        scores = np.asarray([list(scores.values())])

        # controllo che scores abbia risultati numerici come true_relevance:
        # (controllo che elimineremo con la benchmark giusta)
        # print(scores)

        # questo è un controllo dummy: se i documenti recuperati non sono abbastanza,
        # non facciamo alcun controllo reale.
        # Infatti, inizializziamo scores a true_relevance, che è come confrontare true_relevance con sè stesso.
        if len(results) < NUM_R_DOCS:
            scores = true_relevance

        ndcg = ndcg_score(true_relevance, scores)
        print(f"Query numero {i}: {ndcg}")
        media += ndcg

    # Infine calcoliamo la media di tutti i ndcg per l'intero set di query.
    # Così otteniamo un calcolo dell'efficienza dell'IR.
    media = media / len(benchmark)
    print(f"\nNDCG dell'intero IR: {media}")


main()
