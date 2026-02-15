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

    # Flag to mark demo groups that should not be deleted
    is_demo = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_tags_list(self):
        return self.tags.split(',') if self.tags else []

    def get_demo_group_key(self):
        """Identify known demo groups by name."""
        if not self.is_demo:
            return None

        normalized_name = " ".join((self.name or "").lower().split())

        if "board" in normalized_name and "game" in normalized_name and "afternoon" in normalized_name:
            return "board_games_afternoon"
        if "walk" in normalized_name and "talk" in normalized_name and "nature" in normalized_name:
            return "walk_talk_nature_club"

        return None

    def get_demo_base_youth_percentage(self):
        """Return hardcoded base youth percentages for known demo groups."""
        base_youth_by_demo_group = {
            "board_games_afternoon": 75,    # 25% senior, 75% youth
            "walk_talk_nature_club": 25,    # 75% senior, 25% youth
        }

        demo_group_key = self.get_demo_group_key()
        if not demo_group_key:
            return None

        return base_youth_by_demo_group.get(demo_group_key)

    def calculate_youth_percentage(self):
        """Calculate the actual youth percentage based on group members' age categories"""
        from users import User

        # Demo groups use hardcoded base ratios plus demo-only join adjustments.
        if self.is_demo:
            base_youth_percentage = self.get_demo_base_youth_percentage()
            if base_youth_percentage is None:
                return self.youth_percentage

            from flask import has_request_context, session

            # Without a request/user, show the hardcoded base ratio.
            if not has_request_context():
                return base_youth_percentage

            current_user_name = session.get('user_name', None)
            if not current_user_name:
                return base_youth_percentage

            # Apply "joined user" adjustment only when the current user is in the group.
            member = GroupMember.query.filter_by(
                group_id=self.id,
                user_name=current_user_name
            ).first()
            if not member:
                return base_youth_percentage

            current_user = User.query.filter_by(full_name=current_user_name).first()
            if not current_user or not current_user.age_category:
                return base_youth_percentage

            age_category = current_user.age_category.strip().lower()
            base_senior_percentage = 100 - base_youth_percentage

            if age_category.startswith("senior"):
                # If seniors are minority, +4 senior points; otherwise +1.
                senior_delta = 1 if base_senior_percentage >= base_youth_percentage else 4
                adjusted_senior_percentage = min(100, base_senior_percentage + senior_delta)
                return max(0, 100 - adjusted_senior_percentage)

            if age_category.startswith("youth"):
                # If youths are minority, +4 youth points; otherwise +1.
                youth_delta = 1 if base_youth_percentage >= base_senior_percentage else 4
                return min(100, base_youth_percentage + youth_delta)

            return base_youth_percentage

        # Get all members of this group
        members = GroupMember.query.filter_by(group_id=self.id).all()

        if not members:
            return 50  # Default if no members

        youth_count = 0
        senior_count = 0

        for member in members:
            # Find the user by full_name (user_name stores full_name)
            user = User.query.filter_by(full_name=member.user_name).first()
            if user:
                if user.age_category == 'Youth':
                    youth_count += 1
                elif user.age_category == 'Seniors':
                    senior_count += 1

        total_counted = youth_count + senior_count

        if total_counted == 0:
            return 50  # Default if no youth or seniors

        # Calculate percentage of youth
        return int((youth_count / total_counted) * 100)


class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)  # For demo purposes
    buddy_id = db.Column(db.Integer, db.ForeignKey('group_member.id'), nullable=True)
    mood_status = db.Column(db.String(50), default="😊")
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)


class BuddyQuizResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    answer = db.Column(db.String(50), nullable=False)  # new_skills, sharing, conversations, explore
    matched_buddy_name = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


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
