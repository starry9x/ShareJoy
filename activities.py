from extensions import db

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    date = db.Column(db.String(20))
    time = db.Column(db.String(10))
    duration_hours = db.Column(db.Integer)
    duration_minutes = db.Column(db.Integer)
    format_type = db.Column(db.String(20))
    location = db.Column(db.String(100))
    type = db.Column(db.String(50))
    energy = db.Column(db.String(10))
    max_participants = db.Column(db.Integer)
    participants = db.Column(db.Integer)
    tags = db.Column(db.String(200))
    creator = db.Column(db.String(50))
