import os
import re
from newspaper import build
from newspaper.article import ArticleException
from bs4 import BeautifulSoup

def clean_filename(filename):
    # Rimuovi i caratteri non consentiti nei nomi dei file
    return re.sub(r'[<>:"/\\|?*]', '', filename)

# URL base
base_url = 'https://www.repubblica.it/'

# Parole chiave associate a pubblicità
ad_keywords = ['advertising', 'pubblicita', 'ads']

# Specifica le categorie desiderate
categories = ['cronaca', 'economia', 'cultura']

# Itera attraverso le categorie
for category in categories:
    # Costruisci l'URL della categoria
    category_url = f'{base_url}{category}'
    category_news = build(category_url, memoize_articles=False)

    # Crea la cartella per la categoria se non esiste già
    category_folder = f"./{category}"
    os.makedirs(category_folder, exist_ok=True)

    # Itera attraverso gli articoli della categoria
    for article in category_news.articles:
        try:
            # Verifica se l'URL contiene parole chiave associate a pubblicità
            if not any(keyword in article.url.lower() for keyword in ad_keywords):
                # Verifica se l'articolo appartiene alla categoria specifica
                if f'/{category}' in article.url.lower():
                    # Costruisci l'oggetto Article
                    article.build()

                    # Estrai il testo dai tag <p> nella classe 'story__text'
                    soup = BeautifulSoup(article.html, 'html.parser')
                    text_content = '\n'.join([p.get_text(strip=True) for p in soup.select('.story__text p')])

                    # Altre informazioni dell'articolo
                    title = article.title
                    link = article.url
                    publish_date = article.publish_date

                    # Pulisci il nome del file
                    clean_title = clean_filename(title)

                    # Crea e scrivi il file .txt con le informazioni dell'articolo
                    file_path = os.path.join(category_folder, f"{clean_title}.txt")
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(f"{title}\n")
                        file.write(f"{link}\n")
                        file.write(f"{publish_date}\n")
                        file.write(f"{text_content}\n")

        except ArticleException as e:
            print(f"Errore durante il recupero dell'articolo: {e}")
