import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import login_required, login_user, current_user, logout_user, LoginManager
from werkzeug.utils import send_from_directory, secure_filename
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from config import JobApplication, User, db, Config, Resume
from jobs import job_bp
app = Flask(__name__)
app.secret_key="secret"
app.config.from_object(Config)
db.init_app(app)
app.register_blueprint(job_bp)

#uploads
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

#Login
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/jobs')
def show_jobs():
    jobs = [
    {"id": 1, "title": "Software Engineer", "company": "Google", "status": "Applied"},
    {"id": 2, "title": "Data Scientist", "company": "Facebook", "status": "Pending"},
]
    return render_template('jobs.html', jobs=jobs)

@app.route('/')
def home():
    return render_template('home.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password", "danger")
        return render_template("login.html")
    return render_template('login.html')

#foundation for the future if I want to have profiles public
@app.route("/user/<username>")
@login_required
def user():
    return f"Welcome {current_user.username}!"

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("login"))

@app.route("/registration", methods=['GET','POST'])
def registration():
    #print(request.form)
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("Username or email exists!", "danger")
            return redirect(url_for("registration"))

        hashed_password = generate_password_hash(password)

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created! You can now log in.", "success")
        return render_template("login.html")
    return render_template("registration.html")

@app.route("/resume")
@login_required
def resume():
    # Check if a resume file exists
    resume_file = os.listdir(app.config['UPLOAD_FOLDER'])
    if resume_file:
        return render_template('resume.html', resume={'content': resume_file[0]})
    return render_template('resume.html', resume=None)

@app.route('/edit_resume', methods=['GET', 'POST'])
@login_required
def edit_resume():

    if request.method == 'POST':

        if 'file' not in request.files:
            return "No file part", 400

        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400

        if not file.filename.endswith('.pdf'):
            flash( "Please upload a valid PDF file.", 'danger')
            return redirect(url_for('resume'))

        #delete_file()
        filename = secure_filename(f"{current_user.id}_resume.pdf")

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        existing_resume = Resume.query.filter_by(user_id=current_user.id).first()

        if existing_resume:
            existing_resume.filename=filename
            existing_resume.filepath=file_path
        else:
            new_resume = Resume(filename=filename, user_id=current_user.id, file_path=file_path)
            db.session.add(new_resume)

        db.session.commit()
        return redirect(url_for('resume'))
    return render_template('edit_resume.html')

@app.route("/delete_resume",  methods=['GET', 'POST'])
@login_required
def delete_file():
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_path}")
        except OSError as e:
            print(f"Error deleting {file_path}: {e}")
    return render_template('resume.html', resume=None)


with app.app_context():
    #db.drop_all()
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)