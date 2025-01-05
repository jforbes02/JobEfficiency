from flask import Flask, render_template

from config import JobApplication
from jobs import job_bp
app = Flask(__name__)
app.register_blueprint(job_bp)
@app.route('/')

def show_jobs():
    jobs = JobApplication.query.all()
    return render_template('jobs.html', jobs=jobs)
def home():  # put application's code here
    return render_template('home.html')
if __name__ == '__main__':
    app.run(debug=True)
