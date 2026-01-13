from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'  # or MySQL/Postgres

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import the Activity model
from activities import Activity

activities_list = ["Board Games Afternoon"]

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
        num_activities=num_activities
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
