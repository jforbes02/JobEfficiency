from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import login_required, login_user

from config import JobApplication, User, db
from jobs import job_bp
app = Flask(__name__)
app.secret_key="secret"
app.register_blueprint(job_bp)
@app.route('/jobs')
def show_jobs():
    jobs = [
    {"id": 1, "title": "Software Engineer", "company": "Google", "status": "Applied"},
    {"id": 2, "title": "Data Scientist", "company": "Facebook", "status": "Pending"},
]
    return render_template('jobs.html', jobs=jobs)

@app.route('/')
def home():  # put application's code here
    return render_template('home.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user:
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password", "danger")
        return render_template("login.html")
    return render_template('login.html')
@app.route("/user")
def user():
    if "user" in session:
        return f"Welcome {session['user']}!"
    return redirect(url_for("login.html"))

@app.route("/logout")
@login_required
def logout():
    logout.user()
    flash("You have been logged out.", "info")
    return redirect("login.html")

@app.route("/registration")
def registration():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter((User.username == username) | (User.email ==email)).first()
        if existing_user:
            flash("Userame or email exists!", "danger")
            return redirect(url_for("registration"))

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created! login in.", "success")
        return render_template("login.html")
    return render_template("registration.html")

@app.route("/resume")
def resume():
    return render_template("resume.html")
@app.route("/edit_resume")
def edit_resume():
    return render_template("edit_resume.html")


if __name__ == '__main__':
    app.run(debug=True)
