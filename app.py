from flask import Flask, render_template, request, flash
from extensions import db, migrate
from messages import Message, Contact
from activities import Activity
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sharejoy.db'

db.init_app(app)
migrate.init_app(app, db)

app.secret_key = os.urandom(24)


@app.route("/")
def home():
    return render_template("homepage.html", title="Home")

@app.route("/groups")
def groups():
    return render_template("groups.html", title="Groups")

from flask import request, redirect, url_for

@app.route("/messages")
def messages():
    contacts = Contact.query.all()

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
        username = request.form.get("username")
        content = request.form.get("content")
        if username and content:
            new_msg = Message(username=username, content=content, contact_id=contact.id)
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

@app.route("/activities")
def activities():
    activities = Activity.query.filter_by(creator="me").order_by(Activity.date.asc()).all()

    for activity in activities:
        if activity.tags:
            activity.tags = activity.tags.split(",")
        else:
            activity.tags = []

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
    db.session.delete(activity)
    db.session.commit()
    flash(f'Activity "{activity.name}" has been deleted.', "success")
    return redirect(url_for("activities"))

@app.route('/activity/create', methods=['GET', 'POST'])
def activity_create():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        date = request.form.get('date')
        time = request.form.get('time')
        duration_hours = int(request.form.get('duration_hours') or 0)
        duration_minutes = int(request.form.get('duration_minutes') or 0)
        format_type = request.form.get('format_type')
        location = request.form.get('location') or ''
        type_ = request.form.get('type')
        energy = request.form.get('energy')
        max_participants = int(request.form.get('max_participants') or 0)
        tags = request.form.get('tags') or ''

        new_activity = Activity(
            name=name,
            description=description,
            date=date,
            time=time,
            duration_hours=duration_hours,
            duration_minutes=duration_minutes,
            format_type=format_type,
            location=location,
            type=type_,
            energy=energy,
            max_participants=max_participants,
            participants=0,
            tags=tags,
            creator='me'
        )

        db.session.add(new_activity)
        db.session.commit()

        return redirect(url_for('activities'))

    my_activities_count = Activity.query.filter_by(creator="me").count()
    return render_template('activity_create.html',
                           title="Create Activity",
                           num_activities=my_activities_count)

@app.route("/explore") 
def explore(): 
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
            for activity in activities: 
                activity.tags = activity.tags.split(",") if activity.tags else [] 
                
            return render_template("explore.html", activities=activities)

@app.route("/schedule")
def schedule():
    return render_template("schedule.html", title="Schedule")

@app.route("/profile")
def profile():
    return render_template("profile.html", title="Profile")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/forgot-password")
def forgot_password():
    return render_template("forgotpassword.html")

@app.route("/loginpage")
def loginpage():
    return render_template("loginpage.html")


if __name__ == '__main__':
    app.run()
