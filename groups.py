from extensions import db
from datetime import datetime

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)

    # Fields for the design
    image_url = db.Column(db.String(200), default="default_group.jpg")
    tags = db.Column(db.String(200))

    current_participants = db.Column(db.Integer, default=0)
    max_participants = db.Column(db.Integer, default=40)

    # 0 to 100 representing percentage of Youth
    youth_percentage = db.Column(db.Integer, default=50)

    # New fields for buddy system and privacy
    buddy_system_enabled = db.Column(db.Boolean, default=True)
    privacy = db.Column(db.String(20), default="Public")  # Public or Private

    # Owner/creator of the group
    owner = db.Column(db.String(100), nullable=True)  # Username of the creator

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_tags_list(self):
        return self.tags.split(',') if self.tags else []


class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)  # For demo purposes
    buddy_id = db.Column(db.Integer, db.ForeignKey('group_member.id'), nullable=True)
    mood_status = db.Column(db.String(50), default="😊")
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)


class GroupPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class GroupComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('group_post.id'), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class GroupChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)