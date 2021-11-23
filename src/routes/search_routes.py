from flask import Blueprint, jsonify, request
import json,sys,os

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import main


search_routes = Blueprint(name="search", import_name=__name__)


@search_routes.route('/', methods=['POST'])
def search():
    result=main.search(request.form["phrase"])
    return jsonify(result)

