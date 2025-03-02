from flask import Blueprint, jsonify, request, render_template
from .api import find_jobs

job_bp = Blueprint('jobs', __name__, static_folder='static', template_folder='templates')

@job_bp.route('/search')
def jobs_search():
    title = request.args.get('title')
    location = request.args.get('location')
    websites = request.args.get('sites').split(',') if request.args.get('sites') else None

    jobs = find_jobs(title, location, websites)
    return jsonify(jobs)
@job_bp.route('/jobs')
def jobs_page():
    return render_template('jobs.html')