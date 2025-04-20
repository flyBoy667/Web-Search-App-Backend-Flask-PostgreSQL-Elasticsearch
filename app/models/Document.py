from app.conf import db


class DocType(db.Model):
    __tablename__ = "doc_type"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.now(),
        onupdate=db.func.now(),
    )

    documents = db.relationship("Document", back_populates="doc_type")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Document(db.Model):
    __tablename__ = "document"
    doc_id = db.Column(db.Integer, primary_key=True, unique=True)
    doc_name = db.Column(db.String(200))
    doc_content = db.Column(db.String(1000))
    doc_type_id = db.Column(db.Integer, db.ForeignKey("doc_type.id"))

    doc_type = db.relationship("DocType", back_populates="documents")

    doc_format = db.Column(db.String(1000))
    doc_insert_date = db.Column(db.DateTime, default=db.func.now())
    doc_updated_date = db.Column(
        db.DateTime,
        default=db.func.now(),
        onupdate=db.func.now(),
    )
    doc_file_full_path = db.Column(db.String(1000))

    def to_dict(self):
        return {
            "doc_id": self.doc_id,
            "doc_name": self.doc_name,
            "doc_content": self.doc_content,
            "doc_type": self.doc_type.name if self.doc_type else None,
            "doc_format": self.doc_format,
            "doc_insert_date": (
                self.doc_insert_date.isoformat() if self.doc_insert_date else None
            ),
            "doc_updated_date": (
                self.doc_updated_date.isoformat() if self.doc_updated_date else None
            ),
            "doc_file_full_path": self.doc_file_full_path,
        }
