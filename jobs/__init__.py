from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from config import JobApplication, db
from .api import find_jobs

job_bp = Blueprint('jobs', __name__, static_folder='static', template_folder='templates')

@job_bp.route('/search', methods=['GET', 'POST'])
def jobs_search():

    #default
    jobs=[]
    searched=False
    error=None
    if request.method=='POST':
        title = request.form.get('title')
        location = request.form.get('location')
    else:
        title = request.args.get('title')
        location = request.args.get('location')

    if title:
        searched=True
        result=find_jobs(title, location)
        if result["success"]:
            jobs=result["data"].get("data", [])
        else:
            error = result["error"]
    return render_template('jobs.html', jobs=jobs,title=title,location=location,searched=searched,error=error)

@job_bp.route('/save-job', methods=['POST'])
@login_required
def save():
    """
    Saving jobs apps to the database
    """
    title = request.form.get('title')
    company = request.form.get('company')
    location = request.form.get('location')
    job_url = request.form.get('url')

    if not title or not company:
        return redirect(url_for('jobs.html'))

    new_ap=JobApplication(title=title,company=company,status='pending',user_id=current_user.id)

    db.session.add(new_ap)
    db.session.commit()

    flash("Job saved", "success")
    return redirect(url_for('jobs.html'))


@job_bp.route('/my-applications')
@login_required
def my_applications():
    """Display the user's saved job applications"""

    applications = JobApplication.query.filter_by(user_id=current_user.id).all()
    return render_template('my_applications.html', applications=applications)

@job_bp.route('/jobs')
def jobs_page():
    return render_template('jobs.html')