import os
import re
from newspaper import build
from newspaper.article import ArticleException
from bs4 import BeautifulSoup

def clean_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def clean_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    story_text = soup.find(class_='ArticleText_article__text__xr3P1')
    if story_text:
        text = re.sub(r'&nbsp;', ' ', story_text.get_text(separator=' ', strip=True))
        text = text.replace('\xa0', ' ')
        return text
    return None

#base_url_r = 'https://www.repubblica.it/'
base_url = 'https://www.quotidiano.net/'
ad_keywords = ['advertising', 'pubblicita', 'ads']
categories = ['esteri', 'cronaca', 'economia', 'cultura', 'politica', 'scuola', 'salute', 'scienze']

# Crea la cartella notizie se non esiste già
notizie_folder = "./notizie"
os.makedirs(notizie_folder, exist_ok=True)

# Itera attraverso le categorie
for category in categories :
    # Costruisci l'URL della categoria
    category_url = f'{base_url}{category}'
    category_news = build(category_url, memoize_articles=False)

    # Itera attraverso gli articoli della categoria
    for article in category_news.articles:
        try:
            # Verifica se l'URL contiene parole chiave associate a pubblicità
            if not any(keyword in article.url.lower() for keyword in ad_keywords):
                # Costruisci l'oggetto Article
                article.build()

                # Verifica che il link dell'articolo esista nella cartella
                #link_esistente = False
                link_file_path = os.path.join(notizie_folder, f"{clean_filename(article.url)}.txt")
                if os.path.exists(link_file_path):
                    print(f"il file esiste già")

                else: # Se il link non esiste già, salva il link nella cartella
                    # Estrai e pulisci l'HTML mantenendo solo il testo della classe 'story__text'
                    text_content = clean_html(article.html)

                    if text_content is not None:
                        # Altre informazioni dell'articolo
                        title = article.title
                        link = article.url
                        #publish_date = article.publish_date #REPUBBLICA
                        publish_date = article.publish_date.strftime('%Y-%m-%d') if article.publish_date else None


                    # Pulisci il nome del file
                        clean_title = clean_filename(title)

                        link_file_path = os.path.join(notizie_folder, f"{clean_title}.txt")
                        with open(link_file_path, 'w', encoding='utf-8') as file:
                            file.write(f"{title}\n")
                            file.write(f"{link}\n")
                            file.write(f"{publish_date}\n")
                            file.write(f"{text_content}\n")


        except ArticleException as e:
            print(f"Errore durante il recupero dell'articolo: {e}")
