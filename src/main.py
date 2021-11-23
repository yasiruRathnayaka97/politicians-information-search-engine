from core.ios import load_corpus,create_bulk
from core.es import create_index,delete_index,search_query,create_props
from core.process import processs_phrase, extract_query_info,create_query,extract_hits


def init():
    try:
        delete_index()
        docs=load_corpus()
        props=create_props()
        create_index(create_bulk(docs),props)
        return {"status":True}
    except:
        return {"status":False}
    
def search(phrase):
    processed_phrase=processs_phrase(phrase)
    query_info=extract_query_info(processed_phrase,phrase)
    and_query,or_query,simple_query=create_query(query_info)
    and_result=search_query(and_query)
    or_result=search_query(or_query)
    simple_result=search_query(simple_query)
    result=extract_hits(and_result,or_result,simple_result,query_info)
    result["status"]=True
    return result
    try:
        processed_phrase=processs_phrase(phrase)
        query_info=extract_query_info(processed_phrase,phrase)
        and_query,or_query,simple_query=create_query(query_info)
        and_result=search_query(and_query)
        or_result=search_query(or_query)
        simple_result=search_query(simple_query)
        result=extract_hits(and_result,or_result,simple_result,query_info)
        result["status"]=True
        return result
    except:
        return {"status":False}
