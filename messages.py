from extensions import db
from datetime import datetime
import pytz

class Contact(db.Model):

    __table_args__ = (
    db.UniqueConstraint('owner_user_id', 'contact_user_id', name='uq_owner_contact'),
    )

    __tablename__ = 'contact'

    id = db.Column(db.Integer, primary_key=True)

    # Who owns this contact list entry
    owner_user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", name="fk_contact_owner_user_id"),
        nullable=False
    )

    # The registered user being added as a contact
    contact_user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", name="fk_contact_contact_user_id"),
        nullable=False
    )

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

    # Relationships
    owner = db.relationship('User', foreign_keys=[owner_user_id], backref='contacts')
    contact_user = db.relationship('User', foreign_keys=[contact_user_id])

    # Messages sent by the owner to the contact
    messages_sent = db.relationship(
        'Message',
        foreign_keys='Message.sender_id',
        primaryjoin='Contact.owner_user_id == Message.sender_id',
        backref='sender_contact',
        lazy='dynamic'
    )

    # Messages received by the owner from the contact
    messages_received = db.relationship(
        'Message',
        foreign_keys='Message.receiver_id',
        primaryjoin='Contact.owner_user_id == Message.receiver_id',
        backref='receiver_contact',
        lazy='dynamic'
    )

    deleted_history = db.Column(db.Boolean, default=False)

    chat_cleared_at = db.Column(db.DateTime, nullable=True)


    def __repr__(self):
        return f"<Contact owner={self.owner_user_id} contact={self.contact_user_id} display_name={self.display_name}>"
    
    def get_message_count(self):
        """Count all messages between owner and contact"""
        return Message.query.filter(
            ((Message.sender_id == self.owner_user_id) & 
             (Message.receiver_id == self.contact_user_id)) |
            ((Message.sender_id == self.contact_user_id) & 
             (Message.receiver_id == self.owner_user_id))
        ).count()
    
    def get_unread_count(self):
        """Count unread messages received by the owner from this contact"""
        return Message.query.filter(
            (Message.sender_id == self.contact_user_id) &
            (Message.receiver_id == self.owner_user_id) &
            (Message.status != "Read")
        ).count()
    
    @property
    def messages(self):
        sent = list(self.messages_sent)
        received = list(self.messages_received)
        return sorted(sent + received, key=lambda m: m.timestamp, reverse=True)

class Message(db.Model):
    __tablename__ = 'message'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Who sent and received the message (linked to user table)
    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", name="fk_message_sender_id"),
        nullable=False
    )

    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", name="fk_message_receiver_id"),
        nullable=False
    )

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

    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

    @property
    def date_only(self):
        """Convenience property to get just the date portion of the timestamp."""
        return self.timestamp.date() if self.timestamp else None

    def __repr__(self):
        return f"<Message {self.id} sender={self.sender_id} receiver={self.receiver_id} status={self.status}>"
    
