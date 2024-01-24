from whoosh.index import open_dir
from whoosh.qparser.dateparse import DateParserPlugin
from whoosh.qparser import QueryParser

from sklearn.metrics import dcg_score
import numpy as np

# VARIABILI GLOBALI NECESSARIE. TO-DO: Ad un utilizzo più ampio, renderemo la lettura del file benchmark.txt più scalato

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

    results = searcher.search(query, limit=10)
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
def init_scores(results, benchmark, index_of_q):
    scores = {}
    urls = []
    for i in range(results.scored_length()):
        # equivale a results[i].get('url'), ossia accedere ad una lista di dizionari.
        urls.append(results[i]['url'])

    for url in urls:
        if str(url) in benchmark[index_of_q]:
            scores[url] = benchmark[index_of_q].get(url)
        else:
            scores[url] = 0

    return scores


def main():
    query, benchmark = read_benchmark()
    media = 0

    # per ogni query in benchmark (tot= NUM_QUERY) , esegue la ndcg.
    for i in range(len(benchmark)):

        # estrai i risultati per la query i di 7 (=NUM_QUERY)
        results = execute_query(query[i])
        rel_scores = init_scores(results, benchmark, i)

        # estraggo i valori (url, val) dalla query i-esima dal benchmark
        gold_standard = benchmark[i]

        # controllo: se i documenti recuperati non sono abbastanza,
        # se non sono abbastanza, paddo i rimanenti valori con 0
        if len(results) < NUM_R_DOCS:
            rel_scores = list(rel_scores.values())
            rel_scores = (rel_scores + NUM_R_DOCS * [0])[:NUM_R_DOCS]
        else:
            rel_scores = list(rel_scores.values())

        # poi ne estraggo semplicemente la lista di valori ideali per confrontarlo con i valori reali
        # NOTA: effettuiamo conversione con numpy
        gold_standard = np.asarray([list(gold_standard.values())])
        rel_scores = np.asarray([rel_scores])

        # print(f"Calcoliamo la ndg di REALI: {rel_scores}\ne di IDEALI: {gold_standard}")
        dcg = dcg_score(rel_scores, gold_standard)
        idcg = dcg_score(gold_standard, gold_standard)
        ndcg = dcg / idcg

        print(f"Query numero {i}: {ndcg}")
        media += ndcg

    # Infine calcoliamo la media di tutti i ndcg per l'intero set di query.
    # Così otteniamo un calcolo dell'efficienza dell'IR.
    media = media / len(benchmark)
    print(f"\nNDCG dell'intero IR: {media}")


main()
