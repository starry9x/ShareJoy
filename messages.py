from extensions import db
from datetime import datetime
import pytz
from sqlalchemy import exc

class Contact(db.Model):
    __tablename__ = 'contact'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(35), nullable=False)
    phone = db.Column(db.String(8), nullable=False)
    __table_args__ = (db.UniqueConstraint('phone', name='uq_contact_phone'),)
    short_desc = db.Column(db.String(120))
    image_url = db.Column(db.String(200), default='default_contact.jpg')  # Added default
    
    # Relationships
    messages = db.relationship("Message", backref="contact", lazy='dynamic', cascade="all, delete-orphan")
    
    # Additional fields with defaults
    chat_group = db.Column(db.String(50), default='General')  # Added default
    message_status = db.Column(db.String(20), default='Unread')  # Added default
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Added creation timestamp
    last_chat = db.Column(db.DateTime)  # Add this field for last message timestamp
    
    def __repr__(self):
        return f'<Contact {self.name} ({self.phone})>'

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), 
                         nullable=False,
                         default=lambda: datetime.now(pytz.utc),
                         index=True)  # Added index for faster queries
    
    # Foreign key with proper constraints
    contact_id = db.Column(
    db.Integer,
    db.ForeignKey("contact.id", ondelete="CASCADE", name="fk_message_contact"),
    nullable=False)

    # Status tracking
    status = db.Column(db.String(20), default='Delivered')  # e.g., Delivered, Read
    
    @property
    def date_only(self):
        return self.timestamp.date() if self.timestamp else None
    
    def __repr__(self):
        return f'<Message {self.id} from {self.username}>'