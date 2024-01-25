from autocorrect import Speller
from nltk.corpus import wordnet as wn, wordnet
from whoosh.index import open_dir
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.qparser.dateparse import DateParserPlugin
import tkinter as tk

from indexing import add_docs, custom_analyzer


# TO-DO: in questo caso l'input è da terminale, più avanti sarà da GUI
class SearchArticle:
    def __init__(self, master):
        self.master = master
        master.title("Article Search")

        self.query_label = tk.Label(master, text="Inserisci ciò che vuoi cercare:")
        self.query_label.pack()

        self.query_entry = tk.Entry(master)
        self.query_entry.pack()

        self.search_button = tk.Button(master, text="Cerca", command=self.search)
        self.search_button.pack()

        self.results_text = tk.Text(master, height=10, width=50)
        self.results_text.pack()

    # Funzione per ottenere le forme derivate e sinonimi di una parola usando nltk
    def get_related_words(self, word):
        related_words = set()

        # Aggiungi la parola originale
        related_words.add(word)

        # Aggiungi le forme derivate
        analyzer = custom_analyzer()
        tokens = [token.text for token in analyzer(word)]
        related_words.update(tokens)

        # Aggiungi sinonimi
        for syn in wordnet.synsets(word, pos=wn.NOUN, lang='ita'):
            for lemma in syn.lemmas('ita'):
                related_words.add(lemma.name())

        return list(related_words)

    def search(self):
        query=self.query_entry.get()
        #query = input("Inserisci ciò che vuoi cercare (default: contenuto) \nSuggerito: 'Allarmante!': ")

        # Correttore ortografico
        spell = Speller(lang='it')
        spell_word = spell(query)

        if query != spell_word:
            print(f"Forse cercavi {spell_word}")
            query = spell_word

        #Ottieni sinonimi della parola inserita
        synonyms = self.get_related_words(query)

        #Aggiugni la parola originale e i sinonimi alla query
        full_query = f"{' OR '.join(synonyms)}"

        ix = open_dir("indexdir")
        searcher = ix.searcher()
        parser = MultifieldParser(["title", "content"], ix.schema)
        #parser = QueryParser("content", ix.schema)
        parser.add_plugin(DateParserPlugin())
        query = parser.parse(full_query)
        # results = searcher.search(query, limit=20) || results = searcher.search(query, limit=None)
        results = searcher.search(query, limit=None)

        #for i in range(0, len(results)):
         #   print(results[i])
        # print(results[i] for i in list(range(0, 10)))

        self.display_results(results)

    def display_results(self, results):
        self.results_text.delete(1.0, tk.END)  # Pulisci il testo attuale

        for result in results:
            title = result["title"]
            content = result["content"]
            url = result["url"]

        for result in results:
            print(result)

        print(len(results))

        display_text = f"Title: {title}\nContent: {content}\nURL: {url}\n\n"
        self.results_text.insert(tk.END, display_text)



if __name__ == "__main__":
    root = tk.Tk()
    app = SearchArticle(root)
    root.mainloop()