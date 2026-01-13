from flask import Flask, render_template
from extensions import db, migrate
from activities import Activity  # now safe to import

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

@app.route("/messages")
def messages():
    return render_template("messages.html", title="Messages")

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
