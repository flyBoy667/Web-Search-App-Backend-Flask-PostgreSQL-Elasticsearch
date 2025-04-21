from app.conf import app, api
from app.ressources.document_ressources import (
    Document_type_ressource,
    DocumentListRessource,
    DocumentRessource,
    DocumentSearchResource,
)


api.add_resource(DocumentListRessource, "/api/document")
api.add_resource(DocumentRessource, "/api/document/<string:doc_id>")
api.add_resource(Document_type_ressource, "/api/document-type")
api.add_resource(DocumentSearchResource, "/api/document-search")


if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)
