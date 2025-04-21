import os
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=("elastic", "laUGXJbiYGRF3OG4Iida"),
    verify_certs=False,
    request_timeout=30 
)

try:
    if not es.ping():
        raise ValueError("Connection to Elasticsearch failed")
except Exception as e:
    print(f"Elasticsearch connection error: {e}")
    es = None  # Désactive Elasticsearch si la connexion échoue


api = Api(app)
db = SQLAlchemy(app)
