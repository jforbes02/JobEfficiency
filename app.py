import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import login_required, login_user, current_user
from werkzeug.utils import send_from_directory

from config import JobApplication, User, db, Config
from jobs import job_bp
app = Flask(__name__)
app.secret_key="secret"
app.config.from_object(Config)
db.init_app(app)
app.register_blueprint(job_bp)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
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

@app.route("/registration", methods=['GET','POST'])
def registration():
    print(request.form)
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
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
    # Check if a resume file exists
    resume_file = os.listdir(app.config['UPLOAD_FOLDER'])
    if resume_file:
        return render_template('resume.html', resume={'content': resume_file[0]})
    return render_template('resume.html', resume=None)

@app.route('/edit_resume', methods=['GET', 'POST'])
def edit_resume():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.pdf'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            return redirect(url_for('resume'))
        else:
            return "Please upload a valid PDF file.", 400

    return render_template('edit_resume.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']
    if file.filename=='':
        return "No selected file", 400

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        return redirect(url_for('display_pdf', filename=file.filename))


if __name__ == '__main__':
    app.run(debug=True)
