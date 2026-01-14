from extensions import db

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)

    date = db.Column(db.String(50))
    time = db.Column(db.String(50))
    duration = db.Column(db.String(50))
    location = db.Column(db.String(120))

    energy = db.Column(db.String(20))

    participants = db.Column(db.Integer, default=0)
    max_participants = db.Column(db.Integer)

    tags = db.Column(db.String(200))

    format_type = db.Column(db.String(20))
