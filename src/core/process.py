from difflib import  SequenceMatcher
from core.query import advance,simple
import json,os


current_dir = os.path.dirname(os.path.realpath(__file__))
with open(current_dir+"\sets.json", encoding="utf-8") as file:
  sets = json.load(file)

parent_dir = os.path.dirname(os.path.dirname(current_dir))
with open(parent_dir+"\corpus\db.json", encoding="utf-8") as file:
  db = json.load(file)

syn_sets=sets["syn_sets"]
rank_sets=sets["rank_sets"]
agg_sets=sets["agg_sets"]
connect_sets=sets["connect_sets"]
select_and_field_sets=sets["select_and_field_sets"]
field_boost_scores=sets["field_boost_scores"]
puncs=sets["puncs"]
stop_words=sets["stop_words"]
field_types=sets["field_types"]

default_field="biography"
default_size=50
default_select="all"
default_field_value=None
simple_field="biography"
def check_simmilarity(expected,given,threshold=0.6):
    simmilarity=SequenceMatcher(None,expected,given).ratio()
    if(simmilarity>=threshold):
        return True
    else:
        return False

# before query
def processs_phrase(phrase):
    
    processed_phrase=phrase+""
    
    for punc in puncs:
            if(punc in processed_phrase):
                processed_phrase=processed_phrase.replace(punc," ")

    for stop_word in stop_words:
            if((stop_word in processed_phrase) and (stop_word not in connect_sets)):
                processed_phrase=processed_phrase.replace(stop_word," ")

    for replace_term in syn_sets:
        for phrase_term in syn_sets[replace_term]:
            if phrase_term in phrase:
                processed_phrase=processed_phrase.replace(phrase_term,replace_term)

    tokens=processed_phrase.split(" ")
    clean_tokens=[]
    for token in tokens:
        if(len(token)>0):
            clean_tokens.append(token)
    return clean_tokens


def match_field_value(token,sub_field_values):
    fields=db.keys()
    for field in fields:
        for val in db[field]:
            vals=val.split(" ")
            for t in vals:
                if(t not in stop_words and token not in stop_words):
                    if(check_simmilarity(t,token,threshold=0.9)):
                        if(field in sub_field_values):
                            sub_field_values[field]=sub_field_values[field]+" "+t
                        else:
                            sub_field_values[field]=t
                        return True,sub_field_values
    else:
        return False,sub_field_values


def extract_query_info(tokens,phrase):

    query_info={}
    query_info["phrase"]=phrase
    query_info["fields"]=[]  # (field,value)
    query_info["selects"]=[] # (select,size)

    select_or_field_terms=[]
    connect_terms=[]
    size_or_numeric_field_values=[]
    rank_terms=[]
    agg_terms=[]
    field_values=[]
    sub_field_values={}
    for token_index in range(len(tokens)):

            token_identified=False
            token=tokens[token_index]
        
            if(token.isnumeric()):
                token_identified=True
                size_or_numeric_field_values.append((token_index,int(token))) 
            if(not token_identified):
                for connect_set in connect_sets:
                    if(check_simmilarity(connect_sets[connect_set],token)):
                        token_identified=True
                        connect_terms.append((token_index,connect_set)) 
            if(not token_identified):
                for agg_set in agg_sets:
                    if(check_simmilarity(agg_sets[agg_set],token,0.8)):
                        token_identified=True
                        agg_terms.append(agg_set) 
            if(not token_identified):  
                token_identified,sub_field_values=match_field_value(token,sub_field_values)              
            if(not token_identified):
                for select_and_field_set in select_and_field_sets:
                        if(check_simmilarity(select_and_field_sets[select_and_field_set],token)):
                                token_identified=True
                                select_or_field_terms.append((token_index,select_and_field_set))
                                
            if(not token_identified):
                for rank_set in rank_sets:
                        if(check_simmilarity(rank_sets[rank_set],token)):
                            token_identified=True
                            rank_terms.append((token_index,rank_set))
                        
            if(not token_identified):
                field_values.append((token_index,token))
            
    select_or_field_terms.append(None)
    connect_terms.append(None)
    size_or_numeric_field_values.append(None)
    rank_terms.append(None)
    field_values.append(None)

    current_son_index=0
    current_field_value_index=0


    if(len(select_or_field_terms)==1):
        field_values=field_values[0:len(field_values)-1]
        field_values+=size_or_numeric_field_values[0:len(size_or_numeric_field_values)-1]
        field_values.sort(key=lambda value:value[0])
        field_values.append(None)
        current_field_value=field_values[current_field_value_index]
        
        fv=""

        while current_field_value!=None:
            fv=fv+str(current_field_value[1])+" "
            current_field_value_index+=1
            current_field_value=field_values[current_field_value_index]

        query_info["fields"].append((default_field,fv))

    else:
        if(len(rank_terms)==1):
            current_son_index=len(size_or_numeric_field_values)-1
            field_values=field_values[0:len(field_values)-1]
            field_values+=size_or_numeric_field_values[0:len(size_or_numeric_field_values)-1]
            field_values.sort(key=lambda value:value[0])
            field_values.append(None)
        
        for current_sof_index in range(len(select_or_field_terms)):
            current_sof=select_or_field_terms[current_sof_index]
            current_son=size_or_numeric_field_values[current_son_index]
            current_field_value=field_values[current_field_value_index]
            if(current_sof!=None and current_field_value!=None and current_sof[0]>field_values[-2][0]):
                if(len(query_info["fields"])>0):
                    if(current_son!=None):
                        query_info["selects"].append((current_sof[1],current_son[1]))
                    else:
                        query_info["selects"].append((current_sof[1],default_size))
                else:
                    field_values=field_values[0:len(field_values)-1]
                    field_values+=size_or_numeric_field_values[0:len(size_or_numeric_field_values)-1]
                    field_values.sort(key=lambda value:value[0])
                    current_field_value=field_values[current_field_value_index]
                    field_values.append(None)
                    fv=""
                    while current_field_value!=None :
                        fv=fv+str(current_field_value[1])+" "
                        current_field_value_index+=1
                        current_field_value=field_values[current_field_value_index]
                    query_info["fields"].append((current_sof[1],fv))
            else:
                fv=""
                d=1
                for connect_term in connect_terms:
                    if(connect_term!=None and field_values[current_field_value_index]!=None and field_values[current_field_value_index][0]+1==connect_term[0]):
                        d+=1
                        break
                while True:
                    if(current_field_value!=None):
                        fv=fv+str(current_field_value[1])+" "
                        if(field_values[current_field_value_index+1]!=None and (field_values[current_field_value_index+1][0]-current_field_value[0])==d):
                           current_field_value_index+=1
                           current_field_value=field_values[current_field_value_index]
                           d=1
                           for connect_term in connect_terms:
                                    if(connect_term!=None and field_values[current_field_value_index]!=None and field_values[current_field_value_index][0]+1==connect_term[0]):
                                        d+=1
                                        break
                        else:
                            break 
                    else:
                        break

                if(current_sof!=None):   
                    if(current_field_value!=None ):    
                        query_info["fields"].append((current_sof[1],default_field_value if fv=="" else fv))
                    else:
                        query_info["selects"].append((current_sof[1],default_size))
    

    for field in sub_field_values:
        for f in query_info["fields"]:
            if(f[0]==field):
                f[1]=f[1]+" "+str(field,sub_field_values[field])
                break
        else:        
            query_info["fields"].append((field,sub_field_values[field]))
    return clean(query_info,agg_terms)

def clean(query_info,agg_terms):
    cleaned_fields=[]
    search_type="non-bool"
    agg_index=0
    for f in query_info["fields"]:
        if(f[1]==""):
            continue
        cleaned_val=[]
        for t in f[1].split(" "):
                if(field_types[f[0]]=="text"):
                    if(not t.isnumeric()):
                        cleaned_val.append(t)
                else:
                    search_type="bool"
                    if(t.isnumeric()):
                        cleaned_val.append(int(t))
        if(field_types[f[0]]=="text"):
            cleaned_fields.append((f[0]," ".join(cleaned_val)))
        else:
            if("range" in agg_terms and len(cleaned_val)>1 and len(cleaned_val)<3):
                 cleaned_fields.append((f[0],cleaned_val[0],cleaned_val[1]))
            elif("high" in agg_terms and len(cleaned_val)==1):
                 cleaned_fields.append((f[0],None,cleaned_val[0]))
            elif("low" in agg_terms and len(cleaned_val)==1):
                 cleaned_fields.append((f[0],cleaned_val[0],None))
            else:
                if(len(cleaned_val)>0):
                    cleaned_fields.append((f[0],sum(cleaned_val)//len(cleaned_val)))
        query_info["fields"]=cleaned_fields
            
    query_info["search_type"]=search_type
    if("count" in agg_terms):
        result_type="count"
    else:
        result_type="non-count"
    query_info["result_type"]=result_type
    return query_info
    
def create_query(query_info):
    query=[]
    if(query_info["search_type"]=="bool"):
        must_fields=[]
        range_fields=[]
        boost_fields=None
        for qf in query_info["fields"]:
                if(len(qf)==2):
                    must_fields.append(qf)
                else:
                    range_fields.append(qf)
        if(len(range_fields)==0):
            range_fields=None
        if(len(must_fields)==0):
            must_fields=None
    else:
        must_fields=None
        range_fields=None
        boost_fields=[]
        for qf in query_info["fields"]:
                boost_fields.append(qf[0]+"^"+str(field_boost_scores[qf[0]]))
                query.append(qf[1])
        query=" ".join(query) 
    and_query= advance(query=query,boost_fields=boost_fields,must_fields=must_fields,range_fields=range_fields,size=default_size)
    or_query=advance(query=query,boost_fields=boost_fields,must_fields=must_fields,range_fields=range_fields,size=default_size,op="or")
    simple_query=simple(query=query_info["phrase"],field=simple_field)
    return and_query,or_query,simple_query

def extract_hits(and_res,or_res,simple_res,query_info):
    if(and_res["hits"]["total"]["value"]!=0):
        res=and_res
    else:
        if(or_res["hits"]["total"]["value"]!=0):
            res=or_res
        else:
            res=simple_res
            query_info["fields"]=[]
            query_info["selects"]=[("biography",None)]
    if(query_info["result_type"]=="count"):
        return {
            "hits":[{"ගණන":res["hits"]["total"]["value"]}]
        }
    else:
        hits=[]
        selects_and_fields=[]
        for field in query_info["fields"]:
            selects_and_fields.append(field[0])
        if(len(query_info["selects"])==0):
            selects_and_fields=select_and_field_sets.keys()
        else:
            for select in query_info["selects"]:
                selects_and_fields.append(select[0])
        for hit in res["hits"]["hits"]:
            _hit={}
            _hit["Score"]=hit["_score"]
            for sof in selects_and_fields:
                if("." in sof):
                    _sof=sof.split(".")
                    _hit[select_and_field_sets[sof]]=hit["_source"][_sof[0]][_sof[1]]
                else:
                    _hit[select_and_field_sets[sof]]=hit["_source"][sof]

            hits.append(_hit)
        return{
            "hits":hits
        }
    



