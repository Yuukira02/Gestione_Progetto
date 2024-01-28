from threading import Thread
from transformers import pipeline
from searcher import execute_query, Correction
import tkinter as tk


class SearchArticle:
    total_results = None

    def __init__(self, master):
        self.master = master
        master.title("Twinkle")

        # Frame per contenere la query_entry e il search_button
        self.entry_frame = tk.Frame(master, background='#FFDAB9')
        self.entry_frame.grid(row=1, column=0, pady=10, padx=20)

        self.query_label = tk.Label(self.entry_frame, text="Cosa vuoi cercare?", background='#FFDAB9', pady=10,
                                    font=("Times New Roman", 15, "bold"))
        self.query_label.grid(row=0, column=0, columnspan=3, sticky="N")

        self.query_entry = tk.Entry(self.entry_frame, width=40, font=("Arial", 12))
        self.query_entry.grid(row=1, column=0, pady=10, ipady=10, padx=(0, 5), sticky="E")

        self.search_button = tk.Button(self.entry_frame, text="Search", command=self.perform_search, width=10)
        self.search_button.grid(row=1, column=1, pady=10, ipady=5, sticky="W")

        self.check_spelling_var = tk.BooleanVar()
        self.check_spelling = tk.Checkbutton(self.entry_frame, text="Correzione ortografica", background='#FFDAB9',
                                             variable=self.check_spelling_var)
        self.check_spelling.grid(row=2, column=0, pady=10, padx=10, sticky="W")

        self.check_synonyms_var = tk.BooleanVar()
        self.check_synonyms = tk.Checkbutton(self.entry_frame, text="Sinonimi", background='#FFDAB9',
                                             variable=self.check_synonyms_var)
        self.check_synonyms.grid(row=2, column=1, pady=10, padx=10, sticky="W")

        self.correction_label = tk.Label(self.entry_frame, text="", background='#FFDAB9', pady=10, font=("Arial", 9))
        self.correction_label.grid(row=3, column=2, pady=10, padx=10, sticky="N")

        self.results_text = tk.Text(master, height=15, width=40, font=("Arial", 12))
        self.results_text.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="WE")

        self.results_label = tk.Label(master, text="", background='#FFDAB9', font=("Arial", 12))
        self.results_label.grid(row=3, column=0, columnspan=4, sticky="N", padx=20, pady=10)

        self.status_label = tk.Label(master, text="", background='#FFDAB9', pady=10, font=("Times New Roman", 12))
        self.status_label.grid(row=4, column=0, columnspan=4, sticky="N", padx=20, pady=10)


    def perform_search(self):
        SearchArticle.total_results = 0

        self.status_label.config(text="Ricerca in corso...")
        self.status_label.update()

        def perform_search_thread():
            classifier = pipeline("text-classification", model='nlptown/bert-base-multilingual-uncased-sentiment', top_k=2)
            V2 = True
            V3 = False
            spelling = self.check_spelling_var.get()
            synonyms = self.check_synonyms_var.get()
            results = []

            if spelling:
                spelling = True
            if synonyms:
                synonyms = True

            results = execute_query(self.query_entry.get(), classifier, V2, V3, spelling, synonyms)

            # Esegui update_ui solo se la finestra è ancora aperta
            if self.master.winfo_exists():
                self.master.after(0, lambda: self.update_ui(results))

        search_thread = Thread(target=perform_search_thread)
        search_thread.start()

    def update_ui(self, results):
        # Pulisci l'area dei risultati
        self.results_text.delete(1.0, tk.END)

        if results:
            for result in results:
                self.results_text.insert(tk.END, result)
        else:
            self.results_text.insert(tk.END, "Nessun risultato trovato.")

        # Aggiorna la label dei risultati totali (variabile di classe) in modo atomico
        SearchArticle.total_results += len(results)
        current_total_results = SearchArticle.total_results
        self.results_label.config(text=f"Risultati totali: {current_total_results}")
        self.status_label.config(text="Ricerca completata")


        # Aggiorna la label di correzione ortografica solo se l'opzione è abilitata
        if self.check_spelling_var.get():
            corrected_query = self.correct_label(self.query_entry.get())
            if corrected_query != self.query_entry.get():
                self.correction_label.config(text=f"Forse cercavi: {corrected_query}")
            else:
                self.correction_label.config(text="")
        else:
            self.correction_label.config(text="")

    def correct_label(self, query):
        # Implementa la correzione ortografica qui (se necessario)
        # In questo esempio, utilizzo la funzione bypass_correction già presente nel tuo codice
        return " ".join(Correction(word) for word in query.split())


if __name__ == "__main__":
    window = tk.Tk()
    window.configure(background='#FFDAB9')
    window.geometry("1200x550")
    window.grid_columnconfigure(0, weight=1)
    app = SearchArticle(window)
    window.mainloop()
