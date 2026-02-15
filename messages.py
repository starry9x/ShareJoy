from extensions import db
from datetime import datetime
import pytz

class Contact(db.Model):
    __tablename__ = 'contact'  

    id = db.Column(db.Integer, primary_key=True)

    # Who owns this contact list entry
    owner_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # The registered user being added as a contact
    contact_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Custom display name (defaults to registered_name but can be changed)
    display_name = db.Column(db.String(35), nullable=False)

    # Optional notes
    short_desc = db.Column(db.String(120))

    # Status of last message (e.g., "read", "unread")
    message_status = db.Column(db.String(20), default="Unread")

    # When the contact was added
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Timestamp of the most recent message exchanged
    last_chat = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Contact owner={self.owner_user_id} contact={self.contact_user_id} display_name={self.display_name}>"


class Message(db.Model):
    __tablename__ = 'message'   
    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Who sent and received the message (linked to users table)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Message content
    content = db.Column(db.Text, nullable=False)

    # Timestamp of when the message was sent
    timestamp = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(pytz.utc),
        index=True
    )

    # Delivery/read status (e.g., "Sent", "Delivered", "Read")
    status = db.Column(db.String(20), default="Delivered")

    @property
    def date_only(self):
        """Convenience property to get just the date portion of the timestamp."""
        return self.timestamp.date() if self.timestamp else None

    def __repr__(self):
        return f"<Message {self.id} sender={self.sender_id} receiver={self.receiver_id} status={self.status}>"
