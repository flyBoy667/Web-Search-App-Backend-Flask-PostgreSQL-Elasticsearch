from app.conf import db


class DocType(db.Model):
    __tablename__ = "doc_type"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )


class Document(db.Model):
    __tablename__ = "document"
    doc_id = db.Column(db.Integer, primary_key=True, unique=True)
    doc_name = db.Column(db.String(200))
    doc_content = db.Column(db.String(1000))
    doc_type_id = db.Column(db.Integer, db.ForeignKey("doc_type.id"))
    doc_type = db.relationship("DocType", backref="documents")
    doc_format = db.Column(db.String(1000))

    doc_insert_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    doc_updated_date = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    doc_file_full_path = db.Column(db.String(1000))
