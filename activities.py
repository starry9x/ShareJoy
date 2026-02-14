from extensions import db

class Activity(db.Model):
    __tablename__ = "activity"
    
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(50))
    date = db.Column(db.String(20))
    time = db.Column(db.String(10))
    duration_hours = db.Column(db.Integer)
    duration_minutes = db.Column(db.Integer)
    format_type = db.Column(db.String(20))
    energy = db.Column(db.String(10))
    participants = db.Column(db.Integer)
    max_participants = db.Column(db.Integer)
    tags = db.Column(db.String(200))
    location = db.Column(db.String(100))
    
    # Relationship to User
    creator = db.relationship("User", backref="created_activities")


class ActivityParticipant(db.Model):
    __tablename__ = "activity_participants"
    
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    participant = db.relationship("User", foreign_keys=[participant_id], backref="joined_activities")
    activity = db.relationship("Activity", backref="participants_list")
    creator = db.relationship("User", foreign_keys=[creator_id])