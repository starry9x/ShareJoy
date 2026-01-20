from extensions import db
from datetime import datetime, timedelta
import pytz
class Contact(db.Model):
    __tablename__ = 'contact'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    short_desc = db.Column(db.String(120))
    image_url = db.Column(db.String(200))

    # one-to-many relationship
    messages = db.relationship("Message", backref="contact", lazy=True)

    chat_group = db.Column(db.String(50))       # e.g. Family, Friends, Work
    message_status = db.Column(db.String(20))   # e.g. Unread, Read, Archived

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(pytz.utc) + timedelta(hours=1))
    contact_id = db.Column(db.Integer, db.ForeignKey("contact.id"), nullable=True)

