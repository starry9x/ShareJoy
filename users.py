from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string

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
    
    # 🆔 UNIQUE ID SYSTEM
    user_unique_id = db.Column(db.String(10), unique=True, nullable=False)
    
    # 🏆 ACHIEVEMENT TRACKING
    activities_created_count = db.Column(db.Integer, default=0)
    first_activity_completed = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def generate_unique_id():
        """Generate a unique user ID in format: USR-A1B2C3"""
        while True:
            # Generate 6 random alphanumeric characters (mix of letters and numbers)
            chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            unique_id = f"USR-{chars}"
            
            # Check if this ID already exists
            if not User.query.filter_by(user_unique_id=unique_id).first():
                return unique_id
    
    def __repr__(self):
        return f'<User {self.full_name}>'