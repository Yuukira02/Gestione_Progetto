import re
import nltk
from whoosh.index import open_dir, exists_in
from autocorrect import Speller
from whoosh.qparser import MultifieldParser
from whoosh.qparser.dateparse import DateParserPlugin
from nltk.corpus import wordnet as wn
from transformers import pipeline
from indexing import convert_predicted_sentiment, create_index


def format_results(res):
    formatted_results = []
    for r in res:
        title = r.get('title')
        date = r.get('date')
        url = r.get('url')
        content = r.get('content')

        if content is not None:
            # Snippet Articolo
            content = content[:100] + '...'
        else:
            print("Snippet dell'Articolo non disponibile")

        formatted_result = f"Titolo: {title}\n{date}\n{content}\nURL: {url}\n\n"
        formatted_results.append(formatted_result)
    return formatted_results


def disambiguate_terms(terms):
    # controllo iniziale:
    try:
        # Prova a cercare il corpus di WordNet
        nltk.data.find('corpora/wordnet')
    except LookupError:
        # Se non trova il corpus, scaricalo
        nltk.download('wordnet')

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

    tokens = re.split(',|_|-|!| OR | NOT | AND |title:|content:|date:|sentiment:| ', word)
    if len(tokens) > 1:
        # Estendi con synset disambiguati dal contesto
        related_words = disambiguate_terms(tokens)
    else:
        # Aggiungi sinonimi
        for syn in wn.synsets(tokens, pos=wn.NOUN, lang='ita'):
            for lemma in syn.lemmas('ita'):
                related_words.add(lemma.name())

    return list(related_words)


def correction(word):
    # Bypassa la correzione ortografica per la parola chiave "NOT"
    if word.upper() == 'NOT':
        return word
    else:
        # Correttore ortografico
        spell = Speller(lang='it')
        return spell(word)


def execute_query(original_query, classifier, sentiment_analysis, correct_spelling, synonym):
    """ALGORITMO CHE DATA UNA QUERY ESEGUE LE RISPOSTE"""

    if not exists_in("indexdir"):
        print("Sto usando indexer da searcher")
        create_index()

    ix = open_dir("indexdir")
    searcher = ix.searcher()
    q = original_query

    if correct_spelling:
        # Applica la correzione ortografica solo per le parole non booleane
        corrected_query = " ".join(correction(word) for word in q.split())
        q = corrected_query

    if synonym:
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
                q += " AND (sentiment:1)"
            if sentiment == -1:
                q += " AND (sentiment:-1)"
            if sentiment == 0:
                q += " AND (sentiment:0"
            print(q)
    parser = MultifieldParser(["title", "content"], ix.schema)
    parser.add_plugin(DateParserPlugin())
    q = parser.parse(q)

    res = searcher.search(q, limit=None)

    # Formatta i risultati direttamente nella funzione
    # res = format_results(res)

    return res


if __name__ == "__main__":
    sentiment_classifier = pipeline("text-classification",
                                    model='nlptown/bert-base-multilingual-uncased-sentiment', top_k=2)
    V3 = True
    query = input("Inserisci ciò che vuoi cercare (default: contenuto) \nSuggerito: 'Allarmante!': ")
    results = execute_query(query, sentiment_classifier, V3, False, False)
    for result in results:
        print(result['url'])
