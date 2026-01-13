from flask import Flask, render_template
from extensions import db, migrate
from messages import Message, Contact
from activities import Activity

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sharejoy.db'

db.init_app(app)
migrate.init_app(app, db)

activities_list = [
    {
    "name": "Board Games Afternoon",
    "description": "Join me for a fun board games session!",
    "type": "Social",
    "date": "20 Dec 2025",
    "time": "2:00 PM",
    "duration": "2 hours",
    "location": "Community Center Game Room",
    "energy": "Low",
    "participants": 3,
    "max_participants": 8,
    "tags": ["boardgames", "cards", "puzzles", "socializing"]
    }
]


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
    return render_template("messages.html", title="Messages", contacts=contacts)

@app.route("/textchat", methods=["GET", "POST"])
def textchat():
    if request.method == "POST":
        username = request.form.get("username")
        content = request.form.get("content")
        if username and content:
            new_msg = Message(username=username, content=content)
            db.session.add(new_msg)
            db.session.commit()
        return redirect(url_for("textchat"))

    all_messages = Message.query.order_by(Message.timestamp.asc()).all()
    return render_template("textchat.html", messages=all_messages, title="Chat Room")

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
    num_activities = len(activities_list)
    return render_template(
        "activities.html",
        title="Activities",
        num_activities=num_activities,
        activities=activities_list
    )

@app.route("/explore")
def explore():
    return render_template("explore.html", title="Explore")

@app.route("/schedule")
def schedule():
    return render_template("schedule.html", title="Schedule")

@app.route("/profile")
def profile():
    return render_template("profile.html", title="Profile")

if __name__ == '__main__':
    app.run()
