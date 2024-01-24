from whoosh.analysis import LanguageAnalyzer, IntraWordFilter
from whoosh.index import create_in
from whoosh.fields import *
import os


# TO-DO: sarebbe bello renderlo una classe.
def custom_analyzer():
    ana = LanguageAnalyzer("it") | IntraWordFilter(splitwords=True, splitnums=True, mergewords=False, mergenums=False)
    return ana


def format_date(date):
    date = date[0:10]
    if date[4] != "-" and date[7] != 0:
        print("Error: not a valid date")
        exit()
    return date


def add_docs(doc_writer):
    # let us open every textual file our dataset directory
    if not os.path.exists("notizie"):
        os.mkdir("notizie")
    path = "notizie\\"
    filelist = os.listdir(path)
    for f in filelist:
        if f.endswith(".txt"):
            try:
                fileobj = open(path + f, "r", encoding="utf8")
            except Exception as e:
                print(e)
                exit()

            title = fileobj.readline().removesuffix('\n')
            url = fileobj.readline().removesuffix('\n')
            modtime = format_date(fileobj.readline())
            content = fileobj.read().removesuffix('\n')
            fileobj.close()
            doc_writer.add_document(title=title, content=content, url=url, date=modtime)


# indexing
schema = Schema(title=TEXT(stored=True), content=TEXT(analyzer=custom_analyzer()), url=ID(stored=True),
                date=DATETIME(stored=True))

if not os.path.exists("indexdir"):
    os.mkdir("indexdir")

ix = create_in("indexdir", schema)
writer = ix.writer()

add_docs(writer)
writer.commit()

# NOTA per la query: (diretta vs parsata):
# Or([Term("content", "render"), And([Term("title", "shade"), Term("keyword", "animate")])])
# ==
# parser.parse(u"render OR (title:shade keyword:animate)")
