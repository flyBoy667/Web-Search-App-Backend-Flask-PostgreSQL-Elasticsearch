from app.conf import app, api
from app.ressources.document_ressources import (
    Document_list_ressource,
    Document_ressource,
    Document_type_ressource,
)


api.add_resource(Document_list_ressource, "/api/document")
api.add_resource(Document_ressource, "/api/document/<string:doc_id>")
api.add_resource(Document_type_ressource, "/api/document-type")


if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)
