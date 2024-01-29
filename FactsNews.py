import tkinter as tk
from tkinter import ttk
from threading import Thread
from transformers import pipeline
from searcher import execute_query, correction
from ttkthemes import ThemedStyle

class SearchArticle:
    total_results = 0

    def __init__(self, master):
        self.master = master
        master.title("Twinkle")

        style = ThemedStyle(master)
        style.set_theme("breeze")

        master.grid_rowconfigure(1, weight=1)
        master.grid_columnconfigure(0, weight=1)

        self.entry_frame = ttk.Frame(master, padding=30)  # Ridotto il padding
        self.entry_frame.grid(row=0, column=0, sticky="nsew")

        self.status_label = ttk.Label(self.entry_frame, text="Twinkle",
                                      font=("Times New Roman", 40))
        self.status_label.pack(pady=(0, 20))

        self.query_entry = ttk.Entry(self.entry_frame ,width=80, font=("Arial", 12))
        self.query_entry.pack(side="top", pady=(5, 10), ipady=7, padx=10)

        checkbox_button_frame = ttk.Frame(self.entry_frame)
        checkbox_button_frame.pack(side="top", pady=5)  # Modificato il pady

        self.check_spelling_var = tk.BooleanVar()
        self.check_spelling = ttk.Checkbutton(checkbox_button_frame, text="Correzione ortografica",
                                              variable=self.check_spelling_var, style="TCheckbutton")
        self.check_spelling.pack(side="left", pady=5, padx=10)

        self.check_synonyms_var = tk.BooleanVar()
        self.check_synonyms = ttk.Checkbutton(checkbox_button_frame, text="Sinonimi", variable=self.check_synonyms_var,
                                              style="TCheckbutton")
        self.check_synonyms.pack(side="left", pady=5, padx=10)

        self.results_text = tk.Text(master, height=10, width=40, font=("Arial", 12), background="white")  # Imposta height al valore desiderato
        self.results_text.grid(row=1, column=0, padx=5, pady=5, sticky="NWE")

        self.search_button = ttk.Button(self.entry_frame, text="Search", command=self.perform_search, width=10)
        self.search_button.pack(side="top", pady=(0, 10), ipady=5, padx=10)  # Modificato il pady

        self.correction_label = ttk.Label(checkbox_button_frame, text="", font=("Arial", 10))
        self.correction_label.pack(side="top", pady=5, padx=5)  # Imposta i valori di pady e padx desiderati

        self.result_label = ttk.Label(master, text="", font=("Arial", 11))
        self.result_label.grid(row=2, column=0, pady=5)

        self.status_label.configure(style="TLabel")

    def perform_search(self):
        self.result_label.config(text="Ricerca in corso...")

        def perform_search_thread():
            classifier = pipeline("text-classification", model='nlptown/bert-base-multilingual-uncased-sentiment', top_k=2)
            V3 = False
            spelling = self.check_spelling_var.get()
            synonyms = self.check_synonyms_var.get()
            results = execute_query(self.query_entry.get(), classifier, V3, spelling, synonyms)

            formatted_results = []
            for result in results:
                title = result.get('title')
                date = result.get('date')
                url = result.get('url')
                content = result.get('content')

                if content is not None:
                    # Snippet Articolo
                    content = content[:100] + '...'
                else:
                    print("Snippet dell'Articolo non disponibile")

                formatted_result = f"Articolo: {title}\n{content}\n{date}\n{url}\n\n"
                formatted_results.append(formatted_result)

            if self.master.winfo_exists():
                self.master.after(0, lambda: self.update_ui(formatted_results, spelling))

        search_thread = Thread(target=perform_search_thread)
        search_thread.start()

    def update_ui(self, formatted_results, spelling):
        self.results_text.delete(1.0, tk.END)

        if formatted_results:
            for result in formatted_results:
                self.results_text.insert(tk.END, result)
        else:
            self.results_text.insert(tk.END, "Nessun risultato trovato.")

        self.result_label.config(text=f"Risultati totali: {len(formatted_results)}")
        self.result_label.config(text="Ricerca completata")

        corrected_query = self.correct_label(self.query_entry.get())
        if spelling:
            if corrected_query != self.query_entry.get():
                self.correction_label.config(text=f"Forse cercavi: {corrected_query}")
            else:
                self.correction_label.config(text="")
        else:
            self.correction_label.config(text="")

    def correct_label(self, query):
        return " ".join(correction(word) for word in query.split())

if __name__ == "__main__":
    window = tk.Tk()
    window.geometry("1200x550")
    window.grid_columnconfigure(0, weight=2)
    app = SearchArticle(window)
    window.mainloop()
