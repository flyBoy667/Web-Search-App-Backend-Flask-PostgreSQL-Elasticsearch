from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from app.models.Document import DocType, Document
import sqlalchemy
from app.conf import db, es
from flask import request
import werkzeug
import os
from werkzeug.utils import secure_filename
from docx import Document as docx
from PyPDF2 import PdfReader


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
    "doc_name",
    type=str,
    required=True,
    help="The document name is required",
    location="form",
)
document_post_args.add_argument(
    "doc_content",
    type=str,
    required=False,
    help="The document content is required",
    location="form",
)
document_post_args.add_argument(
    "doc_type_id",
    type=int,
    required=True,
    help="The document type ID is required",
    location="form",
)
document_post_args.add_argument(
    "doc_format",
    type=str,
    required=True,
    help="The document format is required",
    location="form",
)
document_post_args.add_argument(
    "doc_file_full_path",
    type=str,
    required=False,
    help="The document file full path is required",
    location="form",
)
document_post_args.add_argument(
    "file",
    type=werkzeug.datastructures.FileStorage,
    location="files",
    required=True,
    help="Le fichier est requis",
)


def extract_text_from_pdf(file_stream):
    try:
        reader = PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"[Erreur lecture PDF] {str(e)}"


def extract_text_from_docx(file_stream):
    try:
        doc = docx(file_stream)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        return f"[Erreur lecture DOCX] {str(e)}"


class DocumentListRessource(Resource):
    def get(self):
        documents = Document.query.all()
        return [doc.to_dict() for doc in documents], 200

    def post(self):
        args = document_post_args.parse_args()

        file = request.files["file"]
        filename = secure_filename(file.filename)
        extension = os.path.splitext(filename)[1].lower()

        if extension == ".pdf":
            file_content = extract_text_from_pdf(file)
        elif extension == ".docx":
            file_content = extract_text_from_docx(file)
        elif extension == ".doc":
            return {
                "message": "Le format .doc n’est pas supporté directement. Convertissez en .docx"
            }, 400
        else:
            return {"message": f"Format de fichier {extension} non supporté"}, 400

        UPLOAD_FOLDER = os.path.join(os.getcwd(), "fichiers")
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        document = Document(
            doc_name=args["doc_name"],
            doc_content=file_content,
            doc_type_id=args["doc_type_id"],
            doc_format=args["doc_format"],
            doc_file_full_path=file_path,
        )

        db.session.add(document)
        db.session.commit()

        if es:
            try:
                es.index(
                    index="documents",
                    id=document.doc_id,
                    body={
                        "doc_name": document.doc_name,
                        "doc_content": document.doc_content,
                        "doc_type_id": document.doc_type_id,
                        "doc_format": document.doc_format,
                        "doc_insert_date": document.doc_insert_date.isoformat(),
                        "doc_updated_date": document.doc_updated_date.isoformat(),
                    },
                )
            except:
                print(f"Failed to index document in Elasticsearch: {e}")

        return document.to_dict(), 201


class DocumentRessource(Resource):
    def get(self, doc_id):
        document = db.get_or_404(Document, doc_id, description="Doc not found")

        if not document:
            return {"message": "Document not found"}, 404

        return document.to_dict(), 200

    def delete(self, doc_id):
        document = db.get_or_404(Document, doc_id, description="Doc not found")
        db.session.delete(document)
        db.session.commit()
        return {"message": "Document deleted successfully"}, 204


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


class DocumentSearchResource(Resource):
    def get(self):
        query = request.args("q", "")

        if not query:
            return {"message": "No search query provided"}, 400

        results = es.search(
            index="documents",
            body={
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["doc_name", "doc_content", "doc_type"],
                    }
                }
            },
        )
        hits = results["hits"]["hits"]
        return [hit["_source"] for hit in hits], 200


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
