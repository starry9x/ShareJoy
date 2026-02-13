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

    def calculate_youth_percentage(self):
        """Calculate the actual youth percentage based on group members' age categories"""
        from users import User

        # For demo groups, calculate a realistic ratio based on total members
        # and whether the current logged-in user is Youth or Senior
        if self.is_demo:
            from flask import session, has_request_context

            # Get total number of members
            total_members = GroupMember.query.filter_by(group_id=self.id).count()

            if total_members == 0:
                return self.youth_percentage  # Use stored value if no members

            # Check if current user is a member and get their age category
            # Only access session if we're in a request context
            current_user_name = session.get('user_name', None) if has_request_context() else None
            current_user_is_youth = False
            current_user_is_senior = False

            if current_user_name:
                user = User.query.filter_by(full_name=current_user_name).first()
                if user:
                    current_user_is_youth = (user.age_category == 'Youth')
                    current_user_is_senior = (user.age_category == 'Seniors')

            # Calculate realistic counts based on the stored percentage and total members
            # Use the stored youth_percentage as a base, then adjust for current user
            base_youth_percentage = self.youth_percentage / 100
            base_youth_count = int(total_members * base_youth_percentage)
            base_senior_count = total_members - base_youth_count

            # If current user is a member, adjust the count to include them
            member = GroupMember.query.filter_by(
                group_id=self.id,
                user_name=current_user_name
            ).first() if current_user_name else None

            if member and (current_user_is_youth or current_user_is_senior):
                # Adjust: reduce demo count by 1, then add current user
                if current_user_is_youth:
                    # Make sure at least 1 youth (the user)
                    youth_count = max(1, base_youth_count)
                    senior_count = total_members - youth_count
                else:  # current_user_is_senior
                    # Make sure at least 1 senior (the user)
                    senior_count = max(1, base_senior_count)
                    youth_count = total_members - senior_count
            else:
                youth_count = base_youth_count
                senior_count = base_senior_count

            # Calculate percentage
            if youth_count + senior_count == 0:
                return 50
            return int((youth_count / (youth_count + senior_count)) * 100)

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