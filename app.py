from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify, abort
from extensions import db, migrate
from messages import Message, Contact
from activities import Activity
from users import User
from datetime import datetime, timedelta, date
from groups import Group, GroupMember, GroupPost, GroupComment, GroupChatMessage
from werkzeug.utils import secure_filename
import os
import pytz
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sharejoy.db'
app.secret_key = "some_random_secret"
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
migrate.init_app(app, db)

with app.app_context():
    db.create_all()

# ============================================
# AUTHENTICATION HELPERS
# ============================================

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('loginpage'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get the currently logged-in user"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def calculate_age_category(date_of_birth):
    """Calculate age category based on date of birth"""
    today = date.today()
    age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    
    if 15 <= age <= 35:
        return 'Youth'
    elif age > 60:
        return 'Seniors'
    else:
        return 'Others'

# ============================================
# AUTHENTICATION ROUTES
# ============================================

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Get form data
        full_name = request.form.get("fullName")
        email = request.form.get("email")
        mobile = request.form.get("mobile")
        dob_str = request.form.get("dob")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmPassword")
        bio = request.form.get("bio", "")
        
        # Validation
        errors = []
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            errors.append("Email already registered. Please use a different email or log in.")
        
        # Check password match
        if password != confirm_password:
            errors.append("Passwords do not match.")
        
        # Parse date of birth
        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        except:
            errors.append("Invalid date of birth.")
            dob = None
        
        # Handle ID card upload
        id_card_file = request.files.get('idCard')
        id_card_filename = None
        
        if id_card_file and id_card_file.filename:
            filename = secure_filename(id_card_file.filename)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            id_card_filename = f"{timestamp}_{filename}"
            id_card_path = os.path.join(app.config['UPLOAD_FOLDER'], id_card_filename)
            id_card_file.save(id_card_path)
        else:
            errors.append("ID card upload is required.")
        
        # If there are errors, show them
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template("signup.html", title="Sign Up")
        
        # Calculate age category
        age_category = calculate_age_category(dob)
        
        # Create new user
        new_user = User(
            full_name=full_name,
            email=email,
            mobile=mobile,
            date_of_birth=dob,
            age_category=age_category,
            bio=bio,
            id_card_filename=id_card_filename
        )
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            
            # Log the user in automatically
            session['user_id'] = new_user.id
            session['user_name'] = new_user.full_name
            
            flash('Account created successfully! Welcome to ShareJoy!', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
            return render_template("signup.html", title="Sign Up")
    
    return render_template("signup.html", title="Sign Up")


@app.route("/loginpage", methods=["GET", "POST"])
def loginpage():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Login successful
            session['user_id'] = user.id
            session['user_name'] = user.full_name
            
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
            return render_template("loginpage.html", title="Login")
    
    return render_template("loginpage.html", title="Login")


@app.route("/logout")
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('loginpage'))


@app.route("/profile")
@login_required
def profile():
    user = get_current_user()
    
    # Format joined date
    joined_date = user.created_at.strftime("%B %Y")
    
    return render_template("profile.html", 
                         title="Profile", 
                         user=user, 
                         joined_date=joined_date)


@app.route("/profile/update", methods=["POST"])
@login_required
def update_profile():
    user = get_current_user()
    
    # Update profile fields
    user.bio = request.form.get("bio", user.bio)
    user.work = request.form.get("work", user.work)
    user.education = request.form.get("education", user.education)
    
    # Handle profile image upload
    if 'profileImage' in request.files:
        profile_image = request.files['profileImage']
        if profile_image and profile_image.filename:
            filename = secure_filename(profile_image.filename)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            profile_image_filename = f"profile_{timestamp}_{filename}"
            profile_image_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_image_filename)
            profile_image.save(profile_image_path)
            user.profile_image = profile_image_filename
    
    try:
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating profile: {str(e)}', 'error')
    
    return redirect(url_for('profile'))


@app.route("/accessibility")
@login_required
def accessibility():
    return render_template("accessibility.html", title="Accessibility Settings")


@app.route("/safetynprivacy")
@login_required
def safetynprivacy():
    return render_template("safetynprivacy.html", title="Safety & Privacy")


@app.route("/achievements")
@login_required
def achievements():
    return render_template("achievements.html", title="Achievements & Progress")


@app.route("/badges")
@login_required
def badges():
    return render_template("badges.html", title="Trophies & Badges")


@app.route("/forgotpassword")
def forgotpassword():
    return render_template("forgotpassword.html")


# ============================================
# MAIN ROUTES
# ============================================

@app.route("/")
@login_required
def home():
    return render_template("homepage.html", title="Home")

# ============================================
# MESSAGES ROUTES
# ============================================

@app.template_filter("sgtime")
def sgtime(dt):
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=pytz.utc)
    sg_tz = pytz.timezone("Asia/Singapore")
    return dt.astimezone(sg_tz).strftime("%d %b %Y %H:%M")


@app.route("/messages")
@login_required
def messages():
    search = request.args.get("search", "")
    status_filter = request.args.get("status")

    query = Contact.query

    if search:
        query = query.filter(
            (Contact.name.ilike(f"%{search}%")) |
            (Contact.phone.ilike(f"%{search}%")) |
            (Contact.short_desc.ilike(f"%{search}%")) |
            (Contact.messages.any(Message.content.ilike(f"%{search}%")))
        )

    if status_filter:
        query = query.filter(Contact.message_status == status_filter)

    contacts = query.all()

    for c in contacts:
        last_msg = (
            Message.query.filter_by(contact_id=c.id)
            .order_by(Message.timestamp.desc())
            .first()
        )
        c.last_chat = last_msg.timestamp if last_msg else None

    contacts.sort(key=lambda c: c.last_chat or 0, reverse=True)

    messages = []
    if search:
        messages_query = Message.query.filter(Message.content.ilike(f"%{search}%"))
        if status_filter:
            messages_query = messages_query.filter(Message.status == status_filter)
        messages = messages_query.order_by(Message.timestamp.desc()).all()

    return render_template("messages.html", contacts=contacts, messages=messages, title="Messages")


@app.route("/textchat/<int:contact_id>", methods=["GET", "POST"])
@login_required
def textchat(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    user = get_current_user()

    if request.method == "POST":
        content = request.form.get("content")
        if content:
            new_msg = Message(username=user.full_name, content=content, contact_id=contact.id)
            db.session.add(new_msg)
            db.session.commit()
        return redirect(url_for("textchat", contact_id=contact.id))

    all_messages = Message.query.filter_by(contact_id=contact.id).order_by(Message.timestamp.asc()).all()
    return render_template("textchat.html", contact=contact, messages=all_messages, title="Chat Room")


@app.route("/create_contact", methods=["GET", "POST"])
@login_required
def create_contact():
    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")
        short_desc = request.form.get("short_desc")

        new_contact = Contact(name=name, phone=phone, short_desc=short_desc)
        db.session.add(new_contact)
        db.session.commit()

        return redirect(url_for("messages"))

    return render_template("create_contact.html", title="Create Contact")


@app.route('/delete_contact/<int:contact_id>', methods=['POST'])
@login_required
def delete_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    flash("Contact deleted successfully!", "contact_deleted")
    return redirect(url_for('messages'))


@app.route('/edit_contact/<int:contact_id>', methods=['GET', 'POST'])
@login_required
def edit_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        short_desc = request.form.get('short_desc', '').strip()

        errors = []
        if not name:
            errors.append("Name is required.")
        elif len(name) > 100:
            errors.append("Name cannot exceed 100 characters.")

        if phone and (len(phone) > 20 or not phone.isdigit()):
            errors.append("Phone must be digits only and max 20 characters.")

        if short_desc and len(short_desc) > 120:
            errors.append("Short description cannot exceed 120 characters.")

        if errors:
            return render_template(
                'edit_contact.html',
                contact=contact,
                errors=errors,
                title="Edit Contact"
            )

        contact.name = name
        contact.phone = phone
        contact.short_desc = short_desc
        db.session.commit()

        return redirect(url_for('messages', status='updated'))

    return render_template('edit_contact.html', contact=contact, title="Edit Contact")


# ============================================
# ACTIVITIES ROUTES
# ============================================

@app.route("/activities")
@login_required
def activities():
    user = get_current_user()
    activities = (Activity.query.filter_by(creator=user.full_name).order_by(Activity.date.asc()).all())

    for activity in activities:
        activity.tags = activity.tags.split(",") if activity.tags else []

        try:
            parsed_date = datetime.strptime(activity.date, "%Y-%m-%d")
        except ValueError:
            parsed_date = datetime.strptime(activity.date, "%d %b %Y")
        activity.display_date = parsed_date.strftime("%d %b %Y")

        try:
            parsed_time = datetime.strptime(activity.time, "%H:%M")
        except ValueError:
            parsed_time = datetime.strptime(activity.time, "%I:%M %p")
        activity.display_time = parsed_time.strftime("%I:%M %p").lstrip("0")

    num_activities = len(activities)

    return render_template(
        "activities.html",
        title="Activities",
        num_activities=num_activities,
        activities=activities
    )


@app.route("/activity/delete/<int:activity_id>", methods=["POST"])
@login_required
def activity_delete(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    user = get_current_user()

    if activity.creator != user.full_name:
        abort(403)

    db.session.delete(activity)
    db.session.commit()
    return redirect(url_for("activities"))


@app.route('/activity/create', methods=['GET', 'POST'])
@login_required
def activity_create():
    user = get_current_user()
    
    if request.method == 'POST':
        name = request.form.get("name")
        description = request.form.get("description")
        format_type = request.form.get("format_type")
        location = request.form.get("location")
        date_input = request.form.get("date")
        time_input = request.form.get("time")
        duration_hours = int(request.form.get("duration_hours", 0))
        duration_minutes = int(request.form.get("duration_minutes", 0))
        type_ = request.form.get("type") or "Other"
        energy = request.form.get("energy") or "Low"
        max_participants = int(request.form.get("max_participants", 0))
        tags = request.form.get("tags") or ""

        if format_type:
            format_type = format_type.title()

        if format_type == "Online":
            location = "Online"

        dt = datetime.strptime(f"{date_input} {time_input}", "%Y-%m-%d %H:%M")
        display_date = dt.strftime("%d %b %Y")
        display_time = dt.strftime("%I:%M %p").lstrip("0")

        new_activity = Activity(
            name=name,
            description=description,
            date=date_input,
            time=time_input,
            duration_hours=duration_hours,
            duration_minutes=duration_minutes,
            format_type=format_type,
            location=location,
            type=type_,
            energy=energy,
            max_participants=max_participants,
            participants=1,
            tags=tags,
            creator=user.full_name,
            join_activity="created"
        )

        db.session.add(new_activity)
        db.session.commit()
        return redirect(url_for('activities'))

    my_activities_count = Activity.query.filter_by(creator=user.full_name).count()
    return render_template('activity_create.html',
                           title="Create Activity",
                           num_activities=my_activities_count)


@app.route('/activities/edit/<int:activity_id>', methods=['GET', 'POST'])
@login_required
def edit_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    user = get_current_user()

    if activity.creator != user.full_name:
        abort(403)

    if request.method == 'POST':
        activity.name = request.form['name']
        activity.description = request.form['description']
        activity.date = request.form['date']
        activity.time = request.form['time']
        activity.duration_hours = request.form['duration_hours']
        activity.duration_minutes = request.form['duration_minutes']
        activity.format_type = request.form['format_type']
        activity.location = request.form['location'] if activity.format_type == 'In-Person' else ''
        activity.type = request.form['type']
        activity.energy = request.form['energy']
        activity.max_participants = request.form['max_participants']

        tags_str = request.form.get('tags', '')
        activity.tags = tags_str

        db.session.commit()
        return redirect(url_for('activities'))

    tags = activity.tags.split(',') if activity.tags else []
    
    my_activities_count = Activity.query.filter_by(creator=user.full_name).count()
    return render_template(
        'activity_edit.html',
        title="Edit Activity",
        num_activities=my_activities_count,
        activity=activity,
        tags=tags
    )


@app.route("/explore")
@login_required
def explore():
    user = get_current_user()
    query = Activity.query

    search = request.args.get("search")
    if search:
        query = query.filter(
            (Activity.name.ilike(f"%{search}%")) |
            (Activity.type.ilike(f"%{search}%")) |
            (Activity.tags.ilike(f"%{search}%"))
        )

    category = request.args.get("category")
    if category:
        query = query.filter_by(type=category)

    energy = request.args.get("energy")
    if energy:
        query = query.filter_by(energy=energy)

    format_type = request.args.get("format")
    if format_type:
        query = query.filter_by(format_type=format_type)

    activities = query.order_by(Activity.date.asc()).all()

    for a in activities:
        a.tags = a.tags.split(",") if a.tags else []

        try:
            parsed_date = datetime.strptime(a.date, "%Y-%m-%d")
        except ValueError:
            parsed_date = datetime.strptime(a.date, "%d %b %Y")
        a.display_date = parsed_date.strftime("%d %b %Y")

        try:
            parsed_time = datetime.strptime(a.time, "%H:%M")
        except ValueError:
            parsed_time = datetime.strptime(a.time, "%I:%M %p")
        a.display_time = parsed_time.strftime("%I:%M %p").lstrip("0")

        if a.creator == user.full_name:
            a.join_activity = "created"
        elif a.participants >= a.max_participants:
            a.join_activity = "max"
        elif a.join_activity == 'true':
            a.join_activity = 'true'
        else:
            a.join_activity = 'false'

    return render_template("explore.html", activities=activities)


@app.route('/update-join', methods=['POST'])
@login_required
def update_join():
    data = request.get_json()
    activity_id = data.get('activity_id')
    join_activity = data.get('join_activity')

    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({'success': False, 'message': 'Activity not found'})

    activity.join_activity = 'true' if join_activity else 'false'
    db.session.commit()

    return jsonify({'success': True})


@app.template_test('in_this_week')
def in_this_week(date):
    if not date:
        return False
    today = datetime.today().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week <= date <= end_of_week


@app.route("/leave-activity/<int:activity_id>", methods=["POST"])
@login_required
def leave_activity(activity_id):
    user = get_current_user()
    activity = Activity.query.get_or_404(activity_id)

    if activity.creator == user.full_name:
        return "", 403

    if activity.join_activity == 'true':
        activity.join_activity = 'false'
        if activity.participants > 0:
            activity.participants -= 1
        db.session.commit()

    return "", 204


@app.route("/schedule")
@login_required
def schedule():
    user = get_current_user()
    activities = Activity.query.order_by(Activity.date.asc()).all()
    today = date.today()

    upcoming_week_activities = []
    other_activities = []
    filtered_activities = []

    for activity in activities:
        is_creator = activity.creator == user.full_name
        is_joined = activity.join_activity == 'true'

        if not (is_creator or is_joined):
            continue

        activity.display_tags = activity.tags.split(",") if activity.tags else []

        try:
            parsed_date = datetime.strptime(activity.date, "%Y-%m-%d")
        except ValueError:
            parsed_date = datetime.strptime(activity.date, "%d %b %Y")

        activity.display_date = parsed_date.strftime("%d %b %Y")
        activity.display_date_obj = parsed_date.date()
        activity.days_until = (activity.display_date_obj - today).days

        if is_creator:
            activity.join_activity = "created"
        elif is_joined:
            activity.join_activity = "true"

        if activity.days_until >= 0:
            filtered_activities.append(activity)

            if activity.days_until <= 7:
                upcoming_week_activities.append(activity)
            else:
                other_activities.append(activity)

    total_activities = len(filtered_activities)
    this_week_activities = len(upcoming_week_activities)
    organizing_activities = len(
        [a for a in filtered_activities if a.creator == user.full_name]
    )

    return render_template(
        "schedule.html",
        title="Schedule",
        total_activities=total_activities,
        this_week_activities=this_week_activities,
        organizing_activities=organizing_activities,
        upcoming_week_activities=upcoming_week_activities,
        other_activities=other_activities
    )


# ==========================================
#  GROUPS ROUTES
# ==========================================

@app.route("/groups")
@login_required
def groups():
    if Group.query.count() == 0:
        group1 = Group(
            name="Board Games Afternoon",
            description="Join us for an afternoon of classic and modern tabletop games! Friendly competition and laughter guaranteed. All skill levels welcome.",
            category="Social",
            youth_percentage=70,
            tags="cards,puzzles,boardgames",
            current_participants=20,
            max_participants=40
        )
        group2 = Group(
            name="Walk & Talk Nature Club",
            description="Gentle walks in neighbourhood parks with relaxed conversations and shared moments in nature.",
            category="Wellness",
            youth_percentage=50,
            tags="Wellness,nature,Community",
            current_participants=24,
            max_participants=40
        )
        db.session.add(group1)
        db.session.add(group2)
        db.session.commit()

    current_user = "Jonathan IV"
    all_groups = Group.query.order_by(Group.created_at.asc()).all()
    my_group_ids = [m.group_id for m in GroupMember.query.filter_by(user_name=current_user).all()]
    available_groups = [g for g in all_groups if g.id not in my_group_ids]
    my_groups = [g for g in all_groups if g.id in my_group_ids]

    return render_template(
        "groups.html",
        title="Community Groups",
        available_groups=available_groups,
        my_groups=my_groups
    )


@app.route("/group/create", methods=["GET", "POST"])
@login_required
def create_group():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        privacy = request.form.get("privacy", "Public")
        tags = request.form.get("tags", "")
        current_user = "Jonathan IV"

        errors = []

        if not name or len(name) < 3:
            errors.append("Group name must be at least 3 characters long.")
        elif len(name) > 100:
            errors.append("Group name cannot exceed 100 characters.")

        if not description or len(description) < 10:
            errors.append("Description must be at least 10 characters long.")
        elif len(description) > 500:
            errors.append("Description cannot exceed 500 characters.")

        if not category:
            errors.append("Please select a category.")

        try:
            max_participants = int(request.form.get("max_participants", 40))
            if max_participants < 2:
                errors.append("Group must allow at least 2 participants.")
            elif max_participants > 500:
                errors.append("Maximum participants cannot exceed 500.")
        except ValueError:
            errors.append("Invalid number for max participants.")
            max_participants = 40

        image_file = request.files.get('group_image')
        image_filename = "default_group.jpg"

        if image_file and image_file.filename:
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            filename = secure_filename(image_file.filename)
            file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

            if file_ext not in allowed_extensions:
                errors.append("Invalid image file type. Please upload PNG, JPG, or GIF.")
            else:
                image_file.seek(0, 2)
                file_size = image_file.tell()
                image_file.seek(0)

                if file_size > 5 * 1024 * 1024:
                    errors.append("Image file size cannot exceed 5MB.")
                else:
                    import uuid
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    upload_folder = os.path.join(app.static_folder, 'images')
                    os.makedirs(upload_folder, exist_ok=True)
                    image_path = os.path.join(upload_folder, unique_filename)
                    image_file.save(image_path)
                    image_filename = unique_filename

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("create_group.html", title="Create Group")

        new_group = Group(
            name=name,
            description=description,
            category=category,
            youth_percentage=50,
            tags=tags if tags else "Community,New",
            current_participants=1,
            max_participants=max_participants,
            privacy=privacy,
            owner=current_user,
            image_url=image_filename
        )
        db.session.add(new_group)
        db.session.commit()

        creator_member = GroupMember(
            group_id=new_group.id,
            user_name=current_user,
            mood_status="😊"
        )
        db.session.add(creator_member)
        db.session.commit()

        flash(f'Group "{name}" has been created!', "success")
        return redirect(url_for("groups"))

    return render_template("create_group.html", title="Create Group")


@app.route("/group/<int:group_id>/about")
@login_required
def group_about(group_id):
    group = Group.query.get_or_404(group_id)
    return render_template("group_about.html", group=group, title=group.name)


@app.route("/group/<int:group_id>/buddy-quiz", methods=["GET", "POST"])
@login_required
def buddy_quiz(group_id):
    group = Group.query.get_or_404(group_id)

    if request.method == "POST":
        session['buddy_answer'] = request.form.get("answer")
        return redirect(url_for("buddy_found", group_id=group_id))

    return render_template("buddy_quiz.html", group=group, title="Find Your Buddy")


@app.route("/group/<int:group_id>/buddy-found")
@login_required
def buddy_found(group_id):
    group = Group.query.get_or_404(group_id)
    current_user = "Jonathan IV"
    existing_member = GroupMember.query.filter_by(group_id=group_id, user_name=current_user).first()

    if not existing_member:
        new_member = GroupMember(
            group_id=group_id,
            user_name=current_user,
            mood_status="😊"
        )
        db.session.add(new_member)
        group.current_participants += 1
        db.session.commit()

    return render_template("buddy_found.html", group=group, title="Buddy Found!")


@app.route("/group/<int:group_id>/chat", methods=["GET", "POST"])
@login_required
def group_chat(group_id):
    group = Group.query.get_or_404(group_id)

    if request.method == "POST":
        username = request.form.get("username", "User")
        content = request.form.get("content")

        if content:
            new_message = GroupChatMessage(
                group_id=group.id,
                username=username,
                content=content
            )
            db.session.add(new_message)
            db.session.commit()

        return redirect(url_for("group_chat", group_id=group_id))

    messages = GroupChatMessage.query.filter_by(group_id=group_id).order_by(GroupChatMessage.timestamp.asc()).all()
    member = GroupMember.query.filter_by(group_id=group_id, user_name="Jonathan IV").first()
    if not member:
        member = GroupMember(group_id=group_id, user_name="Jonathan IV", mood_status="😊")
        db.session.add(member)
        db.session.commit()

    return render_template("group_chat.html", group=group, messages=messages, member=member, title=f"{group.name} - Chat")


@app.route("/group/<int:group_id>/feed", methods=["GET", "POST"])
@login_required
def group_feed(group_id):
    group = Group.query.get_or_404(group_id)

    if request.method == "POST":
        author = request.form.get("author", "User")
        content = request.form.get("content")

        image_file = request.files.get('post_image')
        image_filename = None

        if image_file and image_file.filename:
            import uuid
            filename = secure_filename(image_file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            upload_folder = os.path.join(app.static_folder, 'images')
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, unique_filename)
            image_file.save(image_path)
            image_filename = unique_filename

        if content:
            new_post = GroupPost(
                group_id=group.id,
                author=author,
                content=content,
                image_url=image_filename
            )
            db.session.add(new_post)
            db.session.commit()

        return redirect(url_for("group_feed", group_id=group_id))

    posts = GroupPost.query.filter_by(group_id=group_id).order_by(GroupPost.created_at.desc()).all()

    for post in posts:
        post.comments = GroupComment.query.filter_by(post_id=post.id).order_by(GroupComment.created_at).all()

    member = GroupMember.query.filter_by(group_id=group_id, user_name="Jonathan IV").first()
    if not member:
        member = GroupMember(group_id=group_id, user_name="Jonathan IV")
        db.session.add(member)
        db.session.commit()

    return render_template("group_feed.html", group=group, posts=posts, member=member, title=f"{group.name} - Feed")


@app.route("/group/<int:group_id>/settings")
@login_required
def group_settings(group_id):
    group = Group.query.get_or_404(group_id)
    current_user = "Jonathan IV"
    is_owner = (group.owner == current_user)
    return render_template("group_settings.html", group=group, is_owner=is_owner, title="Group Settings")


@app.route("/group/<int:group_id>/edit", methods=["GET", "POST"])
@login_required
def group_edit(group_id):
    group = Group.query.get_or_404(group_id)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        privacy = request.form.get("privacy", group.privacy)

        errors = []

        if not name or len(name) < 3:
            errors.append("Group name must be at least 3 characters long.")
        elif len(name) > 100:
            errors.append("Group name cannot exceed 100 characters.")

        if not description or len(description) < 10:
            errors.append("Description must be at least 10 characters long.")
        elif len(description) > 500:
            errors.append("Description cannot exceed 500 characters.")

        if not category or len(category) < 2:
            errors.append("Category must be at least 2 characters long.")
        elif len(category) > 50:
            errors.append("Category cannot exceed 50 characters.")

        try:
            max_participants = int(request.form.get("max_participants", group.max_participants))
            if max_participants < 1:
                errors.append("Group must allow at least 1 participant.")
            elif max_participants > 500:
                errors.append("Maximum participants cannot exceed 500.")
        except ValueError:
            errors.append("Invalid number for max participants.")
            max_participants = group.max_participants

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("group_edit.html", group=group, title="Edit Group")

        group.name = name
        group.description = description
        group.category = category
        group.max_participants = max_participants
        group.privacy = privacy

        db.session.commit()
        flash(f'Group "{group.name}" has been updated.', "success")
        return redirect(url_for("group_settings", group_id=group_id))

    return render_template("group_edit.html", group=group, title="Edit Group")


@app.route("/group/<int:group_id>/toggle-buddy", methods=["POST"])
@login_required
def toggle_buddy_system(group_id):
    group = Group.query.get_or_404(group_id)
    group.buddy_system_enabled = not group.buddy_system_enabled
    db.session.commit()
    return redirect(url_for("group_settings", group_id=group_id))


@app.route("/group/<int:group_id>/leave/confirm")
@login_required
def leave_group_confirm(group_id):
    group = Group.query.get_or_404(group_id)
    return render_template("group_leave_confirm.html", group=group, title="Leave Group")


@app.route("/group/<int:group_id>/leave", methods=["POST"])
@login_required
def leave_group(group_id):
    group = Group.query.get_or_404(group_id)
    current_user = "Jonathan IV"

    member = GroupMember.query.filter_by(group_id=group_id, user_name=current_user).first()
    if member:
        db.session.delete(member)
        group.current_participants = max(0, group.current_participants - 1)
        db.session.commit()
        flash(f'You have left "{group.name}".', "success")

    return redirect(url_for("groups"))


@app.route("/group/<int:group_id>/update-mood", methods=["POST"])
@login_required
def update_mood(group_id):
    mood = request.form.get("mood", "😊")
    member = GroupMember.query.filter_by(group_id=group_id, user_name="Jonathan IV").first()
    if member:
        member.mood_status = mood
        db.session.commit()

    return redirect(url_for("group_chat", group_id=group_id))


@app.route("/group/post/<int:post_id>/like", methods=["POST"])
@login_required
def like_post(post_id):
    post = GroupPost.query.get_or_404(post_id)

    if request.is_json:
        data = request.get_json()
        liked = data.get('liked', True)

        if liked:
            post.likes += 1
        else:
            post.likes = max(0, post.likes - 1)

        db.session.commit()
        return jsonify({'success': True, 'likes': post.likes})

    post.likes += 1
    db.session.commit()
    return redirect(url_for("group_feed", group_id=post.group_id))


@app.route("/group/post/<int:post_id>/comment", methods=["POST"])
@login_required
def comment_post(post_id):
    post = GroupPost.query.get_or_404(post_id)

    if request.is_json:
        data = request.get_json()
        author = data.get("author", "User")
        content = data.get("content")

        if content:
            new_comment = GroupComment(
                post_id=post.id,
                author=author,
                content=content
            )
            db.session.add(new_comment)
            db.session.commit()
            return jsonify({'success': True})

        return jsonify({'success': False, 'error': 'No content provided'})

    author = request.form.get("author", "User")
    content = request.form.get("content")

    if content:
        new_comment = GroupComment(
            post_id=post.id,
            author=author,
            content=content
        )
        db.session.add(new_comment)
        db.session.commit()

    return redirect(url_for("group_feed", group_id=post.group_id))


@app.route("/group/message/<int:message_id>/delete", methods=["POST"])
@login_required
def delete_message(message_id):
    message = GroupChatMessage.query.get_or_404(message_id)
    current_user = "Jonathan IV"
    if message.username == current_user:
        db.session.delete(message)
        db.session.commit()
        return jsonify({'success': True})

    return jsonify({'success': False, 'error': 'Unauthorized'}), 403


@app.route("/group/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = GroupPost.query.get_or_404(post_id)
    current_user = "Jonathan IV"
    if post.author == current_user or post.author == "Jane_Tan":
        GroupComment.query.filter_by(post_id=post.id).delete()
        db.session.delete(post)
        db.session.commit()
        return jsonify({'success': True})

    return jsonify({'success': False, 'error': 'Unauthorized'}), 403


@app.route("/group/comment/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment = GroupComment.query.get_or_404(comment_id)
    current_user = "Jonathan IV"
    if comment.author == current_user:
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'success': True})

    return jsonify({'success': False, 'error': 'Unauthorized'}), 403


@app.route("/group/<int:group_id>/delete/confirm")
@login_required
def delete_group_confirm(group_id):
    group = Group.query.get_or_404(group_id)
    return render_template("group_delete_confirm.html", group=group, title="Delete Group")


@app.route("/group/<int:group_id>/delete", methods=["POST"])
@login_required
def delete_group(group_id):
    group = Group.query.get_or_404(group_id)

    GroupMember.query.filter_by(group_id=group_id).delete()
    GroupChatMessage.query.filter_by(group_id=group_id).delete()

    posts = GroupPost.query.filter_by(group_id=group_id).all()
    for post in posts:
        GroupComment.query.filter_by(post_id=post.id).delete()
    GroupPost.query.filter_by(group_id=group_id).delete()

    db.session.delete(group)
    db.session.commit()

    flash(f'Group "{group.name}" has been deleted.', "success")
    return redirect(url_for("groups"))


if __name__ == '__main__':
    app.run(debug=True)