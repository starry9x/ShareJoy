from extensions import db
from datetime import datetime

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    short_desc = db.Column(db.String(120))
    image_url = db.Column(db.String(200))

    # one-to-many relationship
    messages = db.relationship("Message", backref="contact", lazy=True)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    contact_id = db.Column(db.Integer, db.ForeignKey("contact.id"), nullable=True)

