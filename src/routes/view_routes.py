from flask import Blueprint,render_template,request
import os,sys

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import main

view_routes = Blueprint(name="view", import_name=__name__)


@view_routes.route('/', methods=['GET','POST'])
def view():
    res_v=[]
    res_k=[]
    error=None
    not_empty=False
    if(request.method == 'POST'):
        if(request.form['phrase']!=""):
            not_empty=True
            empty=None
            try:
                res=main.search(request.form['phrase'])
                res_k=res["hits"][0].keys()
                res_v=res["hits"]
            except:
                error="සොයා ගැනීමට නොහැක"
    return render_template(f'view.html',len_v=len(res_v),len_k=len(res_k),res_v=res_v,res_k=res_k,error=error,not_empty=not_empty)