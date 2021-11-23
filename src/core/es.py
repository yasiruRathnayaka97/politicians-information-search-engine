from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import configparser,os,json

config = configparser.ConfigParser()
config.read("config.ini")
es = Elasticsearch()
index=config["DEFAULT"]["index"]

current_dir = os.path.dirname(os.path.realpath(__file__))
with open(current_dir+"\sets.json", encoding="utf-8") as file:
  sets = json.load(file)


syn_sets=sets["syn_sets"]

stop_words=sets["stop_words"]


def create_props():
        syns=[]
        stops=stop_words
        for syn in syn_sets:
                syns.append(",".join(syn_sets[syn])+"=>"+syn)
        return {
        "settings": {
        "analysis": {
        "analyzer": {
                "sinhala_analyzer": { 
                "tokenizer": "standard",
                "filter": ["syn","sinhala_stop_words"]
                }
        },
        "filter":{
                "syn": {
                        "type": "synonym",
                        "synonyms": syns
          },
          "sinhala_stop_words": {
            "type": "stop",
            "stopwords": stops
          },
        }
    }
  },
   "mappings":{
       "properties":{
        "name":{
                "type":"text",
                "analyzer":"sinhala_analyzer"
         },
         "party":{
                "type":"text",
                "analyzer":"sinhala_analyzer"
         },
         "district":{
                "type":"text",
                "analyzer":"sinhala_analyzer"
         },
         "gender":{
                "type":"text",
                "analyzer":"sinhala_analyzer"
         },
         "biography":{
                "type":"text",
                "analyzer":"sinhala_analyzer"
         },
         "position":{
                "properties":{
                     "type":{
                                "type":"text",
                                "analyzer":"sinhala_analyzer"
                     } ,
                     "subject":{
                                "type":"text",
                                "analyzer":"sinhala_analyzer"
                     } 
             }
         },
          "contact_information": {
             "properties":{
                     "phone":{
                                "type":"integer"
                     } ,
                     "email":{
                                "type":"text"
                     } 
             }
         },
         "birthday":{
                "type":"date",
                "format": "yyyy-MM-dd"
         },
         "age":{
                "type":"integer"
         }
      }
   }
}

def create_index(docs,props=None):
        if(props):
                es.indices.create(index=index,body=props)
        bulk(es,docs,index=index)
        return
        
 
def search_query(query):
        res=es.search(index=index,body=query)
        return res

def delete_index():
        es.indices.delete(index=index)
        return 








        




