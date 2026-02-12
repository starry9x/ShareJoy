from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    age_category = db.Column(db.String(20), nullable=False)  # Youth, Senior, Others
    password_hash = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    id_card_filename = db.Column(db.String(200), nullable=True)
    profile_image = db.Column(db.String(200), nullable=True)
    
    # Profile fields (initially empty)
    work = db.Column(db.Text, nullable=True)
    education = db.Column(db.Text, nullable=True)
    relationship = db.Column(db.Text, nullable=True)  
    interests = db.Column(db.Text, nullable=True)  
    
    # Stats
    posts_count = db.Column(db.Integer, default=0)
    followers_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.full_name}>'
    