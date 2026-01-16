from flask import Flask, render_template, request
from extensions import db, migrate
from messages import Message, Contact
from activities import Activity

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sharejoy.db'

db.init_app(app)
migrate.init_app(app, db)

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

@app.route('/activity/create')
def activity_create():
    my_activities_count = Activity.query.filter_by(creator="me").count()
    return render_template(
        'activity_create.html',
        title="Activities",
        num_activities=my_activities_count,
        activities=activities
    )
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

if __name__ == '__main__':
    app.run()
