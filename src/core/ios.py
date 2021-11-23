import glob, os
import json
import configparser
from datetime import date

config = configparser.ConfigParser()
config.read("config.ini")

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))

corpus_path=parent_dir+"\corpus"


def load_corpus():
    docs=[]
    for file in os.listdir(corpus_path):
        if file.endswith(".json") and file!="db.json":
                doc_path=os.path.join(corpus_path, file)
                with open(doc_path,encoding="utf8") as doc:
                        doc=json.load(doc)
                        doc["_id"]=os.path.basename(doc_path).split(".")[0]
                        if(doc["birthday"]=="දක්වා නැත"):
                            doc["birthday"]=None
                            doc["age"]=None
                        else:
                            b=list(map(int,doc["birthday"].split("-")))
                            born=date(b[0], b[1], b[2])
                            today=date.today()
                            doc["age"]=today.year - born.year - ((today.month, today.day) < (born.month, born.day))
                docs.append(doc)
    return docs


def create_bulk(docs):
    for doc in docs:
        yield doc
        



