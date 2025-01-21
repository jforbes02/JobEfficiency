from flask import Flask, render_template, request, redirect, url_for, session

from config import JobApplication
from jobs import job_bp
app = Flask(__name__)
app.register_blueprint(job_bp)
@app.route('/job')
def show_jobs():
    jobs = JobApplication.query.all()
    return render_template('jobs.html', jobs=jobs)

@app.route('/')
def home():  # put application's code here
    return render_template('home.html')

@app.route("/login", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        return redirect(url_for("user", usr=user))
    else:
        if "user" in session:
            return redirect(url_for("user"))
        return render_template("login.html")

@app.route("/user")
def user():
    if "user" in session:
        user = session["user"]
        return f"<h1>{user}</h1>"
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("home")


if __name__ == '__main__':
    app.run(debug=True)
