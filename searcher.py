import re
import nltk
from whoosh.index import open_dir, exists_in
from autocorrect import Speller
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.qparser.dateparse import DateParserPlugin
from nltk.corpus import wordnet as wn
from transformers import pipeline
from indexing import convert_predicted_sentiment, create_index


def disambiguate_terms(terms):
    # controllo iniziale:
    try:
        # Prova a cercare il corpus di WordNet
        nltk.data.find('corpora/wordnet')
    except LookupError as e:
        # Se non trova il corpus, scaricalo
        nltk.download('wordnet')

    terms = re.split(',|_|-|!| OR | NOT | AND |title:|content:|date:|sentiment:| ', terms)
    related_words = set()
    for t_i in terms:  # t_i is the target term
        sel_sense = None
        sel_score = 0.0

        for s_ti in wn.synsets(t_i, lang='ita', pos=wn.NOUN):
            score_i = 0.0
            for t_j in terms:  # t_j term in t_i's context window
                if t_i == t_j:
                    continue
                best_score = 0.0
                for s_tj in wn.synsets(t_j, lang='ita', pos=wn.NOUN):
                    temp_score = s_ti.wup_similarity(s_tj)
                    if temp_score > best_score:
                        best_score = temp_score
                score_i = score_i + best_score
            if score_i > sel_score:
                sel_score = score_i
                sel_sense = s_ti
        if sel_sense is not None:
            for sense in sel_sense.lemmas('ita'):
                related_words.add(sense.name())
    return related_words


def get_related_words(word):
    related_words = set()

    tokens = word.split()
    if len(tokens) > 1:
        # Estendi con synset disambiguati dal contesto
        related_words = disambiguate_terms(word)
    else:
        # Aggiungi sinonimi
        for syn in wn.synsets(word, pos=wn.NOUN, lang='ita'):
            for lemma in syn.lemmas('ita'):
                related_words.add(lemma.name())

    return list(related_words)


def Correction(word):
    # Bypassa la correzione ortografica per la parola chiave "NOT"
    if word.upper() == 'NOT':
        return word
    else:
        # Correttore ortografico
        spell = Speller(lang='it')
        return spell(word)


def execute_query(original_query, classifier, query_expansion, sentiment_analysis, correct_spelling, synonim):
    """ALGORITMO CHE DATA UNA QUERY ESEGUE LE RISPOSTE"""

    total = 0

    if not exists_in("indexdir"):
        print("Sto usando indexer da searcher")
        create_index()

    ix = open_dir("indexdir")
    searcher = ix.searcher()
    q = original_query

    if query_expansion:
        if correct_spelling == True:
            # Applica la correzione ortografica solo per le parole non booleane
            corrected_query = " ".join(Correction(word) for word in q.split())
            q = corrected_query

        if synonim == True:
            # Ottieni sinonimi della parola inserita
            synonyms = get_related_words(q)

            # Aggiugni la parola originale e i sinonimi alla query
            if len(synonyms) != 0:
                q = q + " AND (" + f"{' OR '.join(synonyms)}" + ")"
                print(q)  # Debug

    # se stiamo eseguendo la V3 dell'engine, esegui
    if sentiment_analysis:
        if "sentiment" not in original_query:
            # valuta la sentiment di una query per aumentare la capacità espressiva
            prediction = classifier(original_query)
            sentiment = convert_predicted_sentiment(prediction)
            print(sentiment)

            if sentiment == 1:
                q += " AND (sentiment:1 OR sentiment:0)"
            if sentiment == -1:
                q += " AND (sentiment:-1 OR sentiment:0)"
            print(q)
    parser = MultifieldParser(["title", "content"], ix.schema)
    # parser = QueryParser("content", ix.schema)
    parser.add_plugin(DateParserPlugin())
    q = parser.parse(q)

    # results = searcher.search(query, limit=20) || results = searcher.search(query, limit=None)
    res = searcher.search(q, limit=None)

    # Formatta i risultati direttamente nella funzione
    formatted_results = []
    for result in res:
        title = result.get('title')
        date = result.get('date')
        url = result.get('url')
        content = result.get('content')

        if content is not None:
            #Snippet Articolo
            content = content[:100] + '...'
            total +=1
        else:
            print("Snippet dell'Articolo non disponibile")

        formatted_result = f"Titolo: {title}\n{date}\n{content}\nURL: {url}\n\n"
        formatted_results.append(formatted_result)

    print(f"Totale: {total}")

    return formatted_results



if __name__ == "__main__":
    classifier = pipeline("text-classification", model='nlptown/bert-base-multilingual-uncased-sentiment', top_k=2)
    V2 = True
    V3 = False
    query = input("Inserisci ciò che vuoi cercare (default: contenuto) \nSuggerito: 'Allarmante!': ")
    results = execute_query(query, classifier, V2, V3, False, False)
    for result in results:
        print(result)

