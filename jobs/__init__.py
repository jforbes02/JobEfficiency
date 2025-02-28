from flask import Blueprint, jsonify
from .api import find_jobs

job_bp = Blueprint('jobs', __name__, static_folder='static', template_folder='templates')

@job_bp.route('/search/<query>')

def jobs_search(query):
    jobs = find_jobs(query)
    return jsonify(jobs)