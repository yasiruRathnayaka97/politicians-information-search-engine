def advance(query=None,boost_fields=None,op="and",type="cross_fields",sort_fields=None,range_fields=None,must_fields=None,size=None):
    q={}
    if(size is not None):
        q["size"]=size
    if((range_fields is not None) or (must_fields is not None)):
        q["query"]={ 
                        "bool": { 
                        }
                    }
        if(must_fields is not None):
            must=[]
            for must_field in must_fields:
                must.append({"match":{must_field[0]:must_field[1]}})

            q["query"]["bool"]["must"]=must
                
        if(range_fields is not None):
            range=[]
            for range_field in range_fields:
                te={}
                if(range_field[1]!=None):
                    te["gte"]=range_field[1]
                if(range_field[2]!=None):
                    te["lte"]=range_field[2]
                range.append({"range": { range_field[0]:te}})
            q["query"]["bool"]["filter"]=range
    
    else:
       q["query"]={
                    "multi_match" : {
                        "query":      query,
                        "type":       type,
                        "fields":     boost_fields,
                        "operator":   op ,
                        "analyzer":"sinhala_analyzer"
                    }
        }

    if(sort_fields is not None):
        q["sort"]= [
                            {sort_field[0]: {"order" : sort_field[1]}}
                    ]
    return q

def simple(query,field,op="and"):
        q={
            "query": {
                "match": {
                }
            }
            }
        q["query"]["match"][field]={
                    "query": query,
                    "operator": op,
                    "fuzziness": "AUTO"
        }
        
        return q
                


