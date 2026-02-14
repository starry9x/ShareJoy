from extensions import db
from datetime import datetime

class Report(db.Model):
    __tablename__ = 'report'
    
    id = db.Column(db.Integer, primary_key=True)
    reporter_name = db.Column(db.String(100), nullable=False)
    reporter_email = db.Column(db.String(120), nullable=False)
    reporter_age = db.Column(db.Integer, nullable=False)
    reported_user_id = db.Column(db.String(10), nullable=False)  # USR-XXXXXX format
    report_reason = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending/reviewed/resolved
    admin_notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Report {self.id} - User {self.reported_user_id}>'