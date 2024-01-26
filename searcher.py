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
        nltk.data.find('wordnet')
    except LookupError as e:
        nltk.download('wordnet')

    terms = re.split(',|_|-|!| OR | NOT |title:|content:|date: |sentiment: | ', terms)
    related_words = set()
    for t_i in terms:  # t_i is target term
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
        # Estenti con synset disambiguati dal contesto
        related_words = disambiguate_terms(word)
    else:
        # Aggiungi sinonimi
        for syn in wn.synsets(word, pos=wn.NOUN, lang='ita'):
            for lemma in syn.lemmas('ita'):
                related_words.add(lemma.name())

    return list(related_words)


def execute_query(original_query, classifier, query_expansion, sentiment_analysis):
    """ALGORITMO CHE DATA UNA QUERY ESEGUE LE RISPOSTE"""

    if(exists_in("indexdir") == False):
        print("Sto usando indexer da searcher")
        create_index()
    ix = open_dir("indexdir")
    searcher = ix.searcher()
    q = original_query

    if query_expansion:
        # Correttore ortografico
        spell = Speller(lang='it')
        spell_word = spell(q)

        if original_query != spell_word:
            print(f"Forse cercavi {spell_word}")
            q = spell_word
            print(q)

        # Ottieni sinonimi della parola inserita
        synonyms = get_related_words(q)

        # Aggiugni la parola originale e i sinonimi alla query
        if len(synonyms) != 0:
            q = q + " AND (" + f"{' OR '.join(synonyms)}" + ")"
            print(q)

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
    res = searcher.search(q, limit=20)
    return res


# TO-DO: in questo caso l'input è da terminale, più avanti sarà da GUI
if __name__ == "__main__":
    classifier = pipeline("text-classification", model='nlptown/bert-base-multilingual-uncased-sentiment', top_k=2)
    V2 = True
    V3 = False
    query = input("Inserisci ciò che vuoi cercare (default: contenuto) \nSuggerito: 'Allarmante!': ")
    results = execute_query(query, classifier, V2, V3)
    for result in results:
        print(result)
