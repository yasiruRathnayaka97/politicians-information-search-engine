from flask import Flask
from src.routes.search_routes import search_routes
from src.routes.view_routes import view_routes
from src.main import init
import configparser,os

config = configparser.ConfigParser()
config.read("config.ini")
stage= int(config["DEFAULT"]["stage"])


current_dir = os.path.dirname(os.path.realpath(__file__))

templates_path=current_dir+"\\src\\templates"

app = Flask(__name__,template_folder=templates_path)


app.register_blueprint(search_routes, url_prefix="/politicians_search_engine/search")
app.register_blueprint(view_routes, url_prefix="/politicians_search_engine/view")

if(stage<=2):
    init()