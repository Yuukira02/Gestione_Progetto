NOTE PER L'UTILIZZO: 
- il progetto contiene transformers, pacchetto che si può utilizzare solo su ambiente virtuale. Per cui è raccomandato eseguire i file dentro a un ambiente virtuale. 
Comandi utili per anaconda: conda list, conda info --envs, where transformers

PACCHETTI DA INSTALLARE DA TERMINALE (appurato che l'ambiente è virtuale):
pip install transformers
pip install newspaper3k
pip install autocorrect
pip install pytorch


Estratto il file .7z in una cartella (che chiameremo "di_lavoro"), controllare la presenza dei seguenti file: FactsNews.py, searcher.py, indexing.py, ndcg.py, benchmark.txt; infine la sottodirectory "notizie". 

"notizie" è la directory che contiene tutti i file di riferimento su cui l'engine farà indicizzazione e ricerca. 

Eseguire FactsNews per utilizzare il searcher attraverso interfaccia utente. 
Altimenti, se si vuole una ricerca da terminale, eseguire solamente searcher.py. 

Per consultare le prestazioni delle diverse versioni abbiamo utilizzato l'algoritmo di discounted continuative gain, implementato nel file ndcg.py. Si suggerisce di cambiare i valori di V2 e V3 (variabili globali) a true se si intende consultare le prestazioni rispettivamente della V2 (query expansion, spelling correction) e V3 (sentiment analysis). 
  Il codice fa uso di una funzione, execute_query, definita in searcher.py. E' suggerito impostare il valore limit a 20, per maggiori prestazioni, nella seguente riga di codice (132): 
        res = searcher.search(q, limit=20)

