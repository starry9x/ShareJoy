from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify, abort
from extensions import db, migrate
from messages import Message, Contact
from activities import Activity
from datetime import datetime
from groups import Group, GroupMember, GroupPost, GroupComment, GroupChatMessage
import os
import pytz


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sharejoy.db'

db.init_app(app)
migrate.init_app(app, db)

with app.app_context():
    db.create_all()
    
app.secret_key = os.urandom(24)

def get_current_user():
    # TEMP: replace with real login later
    return "me"


@app.template_filter("sgtime")
def sgtime(dt):
    if not dt:
        return ""
    # If naive, assume UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=pytz.utc)
    sg_tz = pytz.timezone("Asia/Singapore")
    return dt.astimezone(sg_tz).strftime("%d %b %Y %H:%M")


@app.route("/")
def home():
    return render_template("homepage.html", title="Home")


@app.route("/messages")
def messages():
    # get query params
    search = request.args.get("search", "")
    filter_type = request.args.get("filter_type", "name")  # NEW: default to name
    chat_filter = request.args.get("chat")
    status_filter = request.args.get("status")

    # start with base query
    query = Contact.query

    # apply search depending on filter_type
    if search:
        if filter_type == "name":
            query = query.filter(Contact.name.ilike(f"%{search}%"))
        elif filter_type == "phone":
            query = query.filter(Contact.phone.ilike(f"%{search}%"))
        elif filter_type == "message":
            query = query.filter(Contact.messages.any(Message.content.ilike(f"%{search}%")))
        else:
            # fallback: search across all fields (your original behavior)
            query = query.filter(
                (Contact.name.ilike(f"%{search}%")) |
                (Contact.short_desc.ilike(f"%{search}%")) |
                (Contact.phone.ilike(f"%{search}%")) |
                (Contact.messages.any(Message.content.ilike(f"%{search}%")))
            )

    # filter by chat group (Family, Friends, Work, etc.)
    if chat_filter:
        query = query.filter(Contact.chat_group == chat_filter)

    # filter by message status (Unread, Read, Archived)
    if status_filter:
        query = query.filter(Contact.message_status == status_filter)

    contacts = query.all()

    # attach last message timestamp to each contact
    for c in contacts:
        last_msg = (
            Message.query.filter_by(contact_id=c.id)
            .order_by(Message.timestamp.desc())
            .first()
        )
        c.last_chat = last_msg.timestamp if last_msg else None

    return render_template("messages.html", contacts=contacts, title="Messages")

@app.route("/textchat/<int:contact_id>", methods=["GET", "POST"])
def textchat(contact_id):
    contact = Contact.query.get_or_404(contact_id)

    if request.method == "POST":
        content = request.form.get("content")
        if content:
            # Always mark sender as "me"
            new_msg = Message(username="me", content=content, contact_id=contact.id)
            db.session.add(new_msg)
            db.session.commit()
        return redirect(url_for("textchat", contact_id=contact.id))

    all_messages = Message.query.filter_by(contact_id=contact.id).order_by(Message.timestamp.asc()).all()
    return render_template("textchat.html", contact=contact, messages=all_messages, title="Chat Room")


@app.route("/create_contact", methods=["GET", "POST"])
def create_contact():
    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")
        short_desc = request.form.get("short_desc")

        # Save to database
        new_contact = Contact(name=name, phone=phone, short_desc=short_desc)
        db.session.add(new_contact)
        db.session.commit()

        return redirect(url_for("messages"))  # back to chat list

    return render_template("create_contact.html", title="Create Contact")

@app.route('/delete_contact/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    return redirect(url_for('messages'))

@app.route('/edit_contact/<int:contact_id>', methods=['GET', 'POST'])
def edit_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    if request.method == 'POST':
        contact.name = request.form.get('name', contact.name)
        contact.phone = request.form.get('phone', contact.phone)
        contact.short_desc = request.form.get('short_desc', contact.short_desc)
        db.session.commit()
        return redirect(url_for('messages'))
    return render_template('edit_contact.html', contact=contact, title="Edit Contact")

# Activities Routes
@app.route("/activities")
def activities():
    current_user = get_current_user()

    activities = (Activity.query.filter_by(creator=current_user).order_by(Activity.date.asc()).all())


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
def activity_delete(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    current_user = get_current_user()

    if activity.creator != current_user:
        abort(403)

    db.session.delete(activity)
    db.session.commit()
    return redirect(url_for("activities"))

@app.route('/activity/create', methods=['GET', 'POST'])
def activity_create():
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

        current_user = get_current_user()

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
            participants=0,
            tags=tags,
            creator=current_user
        )

        db.session.add(new_activity)
        db.session.commit()
        return redirect(url_for('activities'))

    my_activities_count = Activity.query.filter_by(creator="me").count()
    return render_template('activity_create.html',
                           title="Create Activity",
                           num_activities=my_activities_count)

@app.route('/activities/edit/<int:activity_id>', methods=['GET', 'POST'])
def edit_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    current_user = get_current_user()

    if activity.creator != current_user:
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
    
    my_activities_count = Activity.query.filter_by(creator="me").count()
    return render_template(
        'activity_edit.html',
        title="Edit Activity",
        num_activities=my_activities_count,
        activity=activity,
        tags=tags
    )

@app.route("/explore")
def explore():
    current_user = get_current_user()
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

        if a.creator == current_user:
            a.join_activity = "created"
        elif a.participants >= a.max_participants:
            a.join_activity = "max"
        else:
            a.join_activity = "false"

    return render_template("explore.html", activities=activities)

@app.route('/update-join', methods=['POST'])
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

@app.route("/schedule")
def schedule():
    return render_template("schedule.html", title="Schedule")

#end of activites routes

@app.route("/profile")
def profile():
    return render_template("profile.html", title="Profile")


@app.route("/signup")
def signup():
    return render_template("signup.html")

<<<<<<< Updated upstream

@app.route("/forgot-password")
def forgot_password():
    return render_template("forgotpassword.html")


@app.route("/safetynprivacy")
def safety_and_privacy():
    return render_template("safetynprivacy.html", title="Safety & Privacy")


@app.route("/accessibility")
def accessibility():
    return render_template("accessibility.html", title="Accessibility")


=======
@app.route("/safetynprivacy")
def safetynprivacy():
    return render_template("safetynprivacy.html", title="Safety & Privacy")

@app.route("/accessibility")
def accessibility():
    return render_template("accessibility.html", title="Accessibility")

@app.route("/forgotpassword")
def forgot_password():
    return render_template("forgotpassword.html")

>>>>>>> Stashed changes
@app.route("/achievements")
def achievements():
    return render_template("achievements.html")


@app.route("/loginpage")
def loginpage():
    return render_template("loginpage.html")


@app.route("/logout")
def logout():
    return redirect(url_for("loginpage"))

# ==========================================
#  GROUPS ROUTES
# ==========================================

@app.route("/groups")
def groups():
    # --- AUTO-SEEDER: Creates your demo groups if none exist ---
    if Group.query.count() == 0:
        group1 = Group(
            name="Board Games Afternoon",
            description="Join us for an afternoon of classic and modern tabletop games! Friendly competition and laughter guaranteed. All skill levels welcome.",
            category="Social",
            youth_percentage=70,  # 70% Youth
            tags="cards,puzzles,boardgames",
            current_participants=20,
            max_participants=40
        )
        group2 = Group(
            name="Walk & Talk Nature Club",
            description="Gentle walks in neighbourhood parks with relaxed conversations and shared moments in nature.",
            category="Wellness",
            youth_percentage=50,  # 50% Youth
            tags="Wellness,nature,Community",
            current_participants=24,
            max_participants=40
        )
        db.session.add(group1)
        db.session.add(group2)
        db.session.commit()
    # -----------------------------------------------------------

    # Get current user (for demo, using "Jonathan IV")
    current_user = "Jonathan IV"

    # Get all groups
    all_groups = Group.query.order_by(Group.created_at.asc()).all()

    # Get groups where user is a member
    my_group_ids = [m.group_id for m in GroupMember.query.filter_by(user_name=current_user).all()]

    # Separate into available and joined groups
    available_groups = [g for g in all_groups if g.id not in my_group_ids]
    my_groups = [g for g in all_groups if g.id in my_group_ids]

    return render_template(
        "groups.html",
        title="Community Groups",
        available_groups=available_groups,
        my_groups=my_groups
    )

@app.route("/group/create", methods=["GET", "POST"])
def create_group():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        privacy = request.form.get("privacy", "Public")
        tags = request.form.get("tags", "")
        current_user = "Jonathan IV"

        # Server-side validation
        errors = []

        # Validate group name
        if not name or len(name) < 3:
            errors.append("Group name must be at least 3 characters long.")
        elif len(name) > 100:
            errors.append("Group name cannot exceed 100 characters.")

        # Validate description
        if not description or len(description) < 10:
            errors.append("Description must be at least 10 characters long.")
        elif len(description) > 500:
            errors.append("Description cannot exceed 500 characters.")

        # Validate category
        if not category:
            errors.append("Please select a category.")

        # Validate max participants
        try:
            max_participants = int(request.form.get("max_participants", 40))
            if max_participants < 2:
                errors.append("Group must allow at least 2 participants.")
            elif max_participants > 500:
                errors.append("Maximum participants cannot exceed 500.")
        except ValueError:
            errors.append("Invalid number for max participants.")
            max_participants = 40

        # Handle image upload with validation
        image_file = request.files.get('group_image')
        image_filename = "default_group.jpg"

        if image_file and image_file.filename:
            import os
            from werkzeug.utils import secure_filename

            # Validate file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            filename = secure_filename(image_file.filename)
            file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

            if file_ext not in allowed_extensions:
                errors.append("Invalid image file type. Please upload PNG, JPG, or GIF.")
            else:
                # Validate file size (5MB max)
                image_file.seek(0, 2)  # Seek to end
                file_size = image_file.tell()
                image_file.seek(0)  # Reset to beginning

                if file_size > 5 * 1024 * 1024:
                    errors.append("Image file size cannot exceed 5MB.")
                else:
                    # Generate unique filename and save
                    import uuid
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"

                    upload_folder = os.path.join(app.static_folder, 'images')
                    os.makedirs(upload_folder, exist_ok=True)

                    image_path = os.path.join(upload_folder, unique_filename)
                    image_file.save(image_path)
                    image_filename = unique_filename

        # If there are validation errors, flash them and return to form
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("create_group.html", title="Create Group")

        # Create new group with the creator as owner
        new_group = Group(
            name=name,
            description=description,
            category=category,
            youth_percentage=50,
            tags=tags if tags else "Community,New",
            current_participants=1,
            max_participants=max_participants,
            privacy=privacy,
            owner=current_user,  # Set the owner
            image_url=image_filename
        )
        db.session.add(new_group)
        db.session.commit()

        # Add creator as a member
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


# ==========================================
#  GROUP INTERACTION FLOW
# ==========================================

@app.route("/group/<int:group_id>/about")
def group_about(group_id):
    group = Group.query.get_or_404(group_id)
    return render_template("group_about.html", group=group, title=group.name)


@app.route("/group/<int:group_id>/buddy-quiz", methods=["GET", "POST"])
def buddy_quiz(group_id):
    group = Group.query.get_or_404(group_id)

    if request.method == "POST":
        # Store the user's answers (for now just simulate)
        session['buddy_answer'] = request.form.get("answer")
        return redirect(url_for("buddy_found", group_id=group_id))

    return render_template("buddy_quiz.html", group=group, title="Find Your Buddy")


@app.route("/group/<int:group_id>/buddy-found")
def buddy_found(group_id):
    group = Group.query.get_or_404(group_id)

    # Add user as a member when they complete the buddy matching
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

    # For demo: get or create a member for current user
    member = GroupMember.query.filter_by(group_id=group_id, user_name="Jonathan IV").first()
    if not member:
        member = GroupMember(group_id=group_id, user_name="Jonathan IV", mood_status="😊")
        db.session.add(member)
        db.session.commit()

    return render_template("group_chat.html", group=group, messages=messages, member=member, title=f"{group.name} - Chat")


@app.route("/group/<int:group_id>/feed", methods=["GET", "POST"])
def group_feed(group_id):
    group = Group.query.get_or_404(group_id)

    if request.method == "POST":
        author = request.form.get("author", "User")
        content = request.form.get("content")

        # Handle image upload
        image_file = request.files.get('post_image')
        image_filename = None

        if image_file and image_file.filename:
            import os
            from werkzeug.utils import secure_filename
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

    # Load comments for each post
    for post in posts:
        post.comments = GroupComment.query.filter_by(post_id=post.id).order_by(GroupComment.created_at).all()

    # For demo: get or create a member for current user
    member = GroupMember.query.filter_by(group_id=group_id, user_name="Jonathan IV").first()
    if not member:
        member = GroupMember(group_id=group_id, user_name="Jonathan IV")
        db.session.add(member)
        db.session.commit()

    return render_template("group_feed.html", group=group, posts=posts, member=member, title=f"{group.name} - Feed")


@app.route("/group/<int:group_id>/settings")
def group_settings(group_id):
    group = Group.query.get_or_404(group_id)
    current_user = "Jonathan IV"
    is_owner = (group.owner == current_user)
    return render_template("group_settings.html", group=group, is_owner=is_owner, title="Group Settings")


@app.route("/group/<int:group_id>/edit", methods=["GET", "POST"])
def group_edit(group_id):
    group = Group.query.get_or_404(group_id)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        privacy = request.form.get("privacy", group.privacy)

        # Server-side validation
        errors = []

        # Validate group name
        if not name or len(name) < 3:
            errors.append("Group name must be at least 3 characters long.")
        elif len(name) > 100:
            errors.append("Group name cannot exceed 100 characters.")

        # Validate description
        if not description or len(description) < 10:
            errors.append("Description must be at least 10 characters long.")
        elif len(description) > 500:
            errors.append("Description cannot exceed 500 characters.")

        # Validate category
        if not category or len(category) < 2:
            errors.append("Category must be at least 2 characters long.")
        elif len(category) > 50:
            errors.append("Category cannot exceed 50 characters.")

        # Validate max participants
        try:
            max_participants = int(request.form.get("max_participants", group.max_participants))
            if max_participants < 1:
                errors.append("Group must allow at least 1 participant.")
            elif max_participants > 500:
                errors.append("Maximum participants cannot exceed 500.")
        except ValueError:
            errors.append("Invalid number for max participants.")
            max_participants = group.max_participants

        # If there are validation errors, flash them and return to form
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("group_edit.html", group=group, title="Edit Group")

        # Update group with validated data
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
def toggle_buddy_system(group_id):
    group = Group.query.get_or_404(group_id)
    group.buddy_system_enabled = not group.buddy_system_enabled
    db.session.commit()
    return redirect(url_for("group_settings", group_id=group_id))


@app.route("/group/<int:group_id>/leave/confirm")
def leave_group_confirm(group_id):
    group = Group.query.get_or_404(group_id)
    return render_template("group_leave_confirm.html", group=group, title="Leave Group")


@app.route("/group/<int:group_id>/leave", methods=["POST"])
def leave_group(group_id):
    group = Group.query.get_or_404(group_id)
    current_user = "Jonathan IV"

    # Remove user from group members
    member = GroupMember.query.filter_by(group_id=group_id, user_name=current_user).first()
    if member:
        db.session.delete(member)
        group.current_participants = max(0, group.current_participants - 1)
        db.session.commit()
        flash(f'You have left "{group.name}".', "success")

    return redirect(url_for("groups"))


@app.route("/group/<int:group_id>/update-mood", methods=["POST"])
def update_mood(group_id):
    mood = request.form.get("mood", "😊")

    member = GroupMember.query.filter_by(group_id=group_id, user_name="Jonathan IV").first()
    if member:
        member.mood_status = mood
        db.session.commit()

    return redirect(url_for("group_chat", group_id=group_id))


@app.route("/group/post/<int:post_id>/like", methods=["POST"])
def like_post(post_id):
    post = GroupPost.query.get_or_404(post_id)

    # Handle JSON request from fetch API
    if request.is_json:
        data = request.get_json()
        liked = data.get('liked', True)

        if liked:
            post.likes += 1
        else:
            post.likes = max(0, post.likes - 1)

        db.session.commit()
        return jsonify({'success': True, 'likes': post.likes})

    # Fallback for form submission
    post.likes += 1
    db.session.commit()
    return redirect(url_for("group_feed", group_id=post.group_id))


@app.route("/group/post/<int:post_id>/comment", methods=["POST"])
def comment_post(post_id):
    post = GroupPost.query.get_or_404(post_id)

    # Handle JSON request from fetch API
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

    # Fallback for form submission
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
def delete_message(message_id):
    message = GroupChatMessage.query.get_or_404(message_id)

    # Only allow deletion of own messages
    current_user = "Jonathan IV"
    if message.username == current_user:
        db.session.delete(message)
        db.session.commit()
        return jsonify({'success': True})

    return jsonify({'success': False, 'error': 'Unauthorized'}), 403


@app.route("/group/post/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    post = GroupPost.query.get_or_404(post_id)

    # Only allow deletion of own posts
    current_user = "Jonathan IV"
    if post.author == current_user or post.author == "Jane_Tan":
        # Delete all comments first
        GroupComment.query.filter_by(post_id=post.id).delete()

        # Delete the post
        db.session.delete(post)
        db.session.commit()
        return jsonify({'success': True})

    return jsonify({'success': False, 'error': 'Unauthorized'}), 403


@app.route("/group/comment/<int:comment_id>/delete", methods=["POST"])
def delete_comment(comment_id):
    comment = GroupComment.query.get_or_404(comment_id)

    # Only allow deletion of own comments
    current_user = "Jonathan IV"
    if comment.author == current_user:
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'success': True})

    return jsonify({'success': False, 'error': 'Unauthorized'}), 403


@app.route("/group/<int:group_id>/delete/confirm")
def delete_group_confirm(group_id):
    group = Group.query.get_or_404(group_id)
    return render_template("group_delete_confirm.html", group=group, title="Delete Group")


@app.route("/group/<int:group_id>/delete", methods=["POST"])
def delete_group(group_id):
    group = Group.query.get_or_404(group_id)

    # Delete all related data
    GroupMember.query.filter_by(group_id=group_id).delete()
    GroupChatMessage.query.filter_by(group_id=group_id).delete()

    # Delete posts and their comments
    posts = GroupPost.query.filter_by(group_id=group_id).all()
    for post in posts:
        GroupComment.query.filter_by(post_id=post.id).delete()
    GroupPost.query.filter_by(group_id=group_id).delete()

    # Delete the group
    db.session.delete(group)
    db.session.commit()

    flash(f'Group "{group.name}" has been deleted.', "success")
    return redirect(url_for("groups"))


if __name__ == '__main__':
    app.run(debug=True)