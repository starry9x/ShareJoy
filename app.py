from flask import Flask, render_template
app = Flask(__name__)
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
    return render_template("activities.html", title="Activities")
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