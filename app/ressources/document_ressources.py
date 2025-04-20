from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from app.models.Document import DocType, Document
import sqlalchemy
from app.conf import db
from flask import request
import werkzeug
import os
from werkzeug.utils import secure_filename


# document_fields = {
#     "doc_id": fields.Integer,
#     "doc_name": fields.String,
#     "doc_content": fields.String,
#     "doc_type_id": fields.String,
#     "doc_type": fields.String,
#     "doc_format": fields.String,
#     "doc_insert_date": fields.String,
#     "doc_updated_date": fields.String,
#     "doc_file_full_path": fields.String,
# }

document_post_args = reqparse.RequestParser()
document_post_args.add_argument(
    "doc_name", type=str, required=True, help="The document name is required"
)
document_post_args.add_argument(
    "doc_content", type=str, required=True, help="The document content is required"
)
document_post_args.add_argument(
    "doc_type_id", type=int, required=True, help="The document type ID is required"
)
document_post_args.add_argument(
    "doc_format", type=str, required=True, help="The document format is required"
)
document_post_args.add_argument(
    "doc_file_full_path",
    type=str,
    required=True,
    help="The document file full path is required",
)
document_post_args.add_argument(
    "file", type=werkzeug.datastructures.FileStorage, location='files', required=True, help="Le fichier est requis"
)


class Document_ressource(Resource):
    def get(self):
        documents = Document.query.all()
        return [doc.to_dict() for doc in documents], 200

    def post(self):
        args = document_post_args.parse_args()
        file = request.files['file']
        
        # Traitez le fichier ici, par exemple, en l'enregistrant
        filename = secure_filename(file.filename)
        file.save(os.path.join('/fichiers/', filename))
        
        # Créez le document avec les autres arguments
        document = Document(
            doc_name=args['doc_name'],
            doc_content=args['doc_content'],
            doc_type_id=args['doc_type_id'],
            doc_format=args['doc_format'],
            doc_file_full_path=filename
        )
        
        db.session.add(document)
        db.session.commit()
        return document.to_dict(), 201


document_type_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "description": fields.String,
    "created_at": fields.String,
    "updated_at": fields.String,
}

document_type_post_args = reqparse.RequestParser()
document_type_post_args.add_argument(
    "name", type=str, required=True, help="Le nom du type de document est requis"
)
document_type_post_args.add_argument(
    "description",
    type=str,
    required=True,
    help="La description du type de document est requise",
)


class Document_type_ressource(Resource):
    @marshal_with(document_type_fields)
    def get(self):
        document_types = DocType.query.all()
        return document_types, 200

    @marshal_with(document_type_fields)
    def post(self):
        args = document_type_post_args.parse_args()
        document_type = DocType(**args)
        db.session.add(document_type)
        db.session.commit()
        return document_type, 201
