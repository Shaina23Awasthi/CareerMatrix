from flask import Flask, render_template, request
from models import db, Student, College, Job
from datetime import datetime
import os

app = Flask(__name__)

# ✅ Correct database path (important for Render)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super_secret_key'

db.init_app(app)

# ❌ Do NOT run db.create_all() on Render startup
# with app.app_context():
#     db.create_all()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/colleges', methods=['GET'])
def colleges():
    location = request.args.get('location')
    course = request.args.get('course')
    sort_by = request.args.get('sort_by')

    query = College.query

    if location:
        query = query.filter(College.location.ilike(f'%{location}%'))
    if course:
        query = query.filter(College.course.ilike(f'%{course}%'))

    if sort_by == 'fees_low_high':
        query = query.order_by(College.fees.asc())
    elif sort_by == 'rating_high_low':
        query = query.order_by(College.rating.desc().nulls_last())

    colleges = query.all()
    return render_template('colleges.html', colleges=colleges)


@app.route('/jobs', methods=['GET'])
def jobs():
    education = request.args.get('education')
    job_type = request.args.get('job_type')
    location = request.args.get('location')
    timeframe = request.args.get('timeframe')

    query = Job.query

    if education:
        query = query.filter(Job.education_required.ilike(f'%{education}%'))
    if job_type:
        query = query.filter(Job.job_type.ilike(f'%{job_type}%'))
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))

    now = datetime.utcnow()
    jobs_list = query.all()
    filtered_jobs = []

    for job in jobs_list:
        if job.last_date:
            days_left = (job.last_date - now).days
            if days_left < 0:
                job.status = 'Expired'
            elif days_left <= 30:
                job.status = 'Upcoming'
            else:
                job.status = 'Active'
        else:
            job.status = 'Active'

        if timeframe == 'active' and job.status != 'Active':
            continue
        if timeframe == 'upcoming' and job.status != 'Upcoming':
            continue

        filtered_jobs.append(job)

    return render_template('jobs.html', jobs=filtered_jobs)


@app.route('/job/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('job_detail.html', job=job)


@app.route('/college/<int:college_id>')
def college_detail(college_id):
    college = College.query.get_or_404(college_id)
    return render_template('college_detail.html', college=college)


@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if request.method == 'POST':
        name = request.form.get('name')
        education_level = request.form.get('education_level')
        interests = request.form.get('interests')
        location = request.form.get('location')

        recommended_careers = set()
        recommended_courses = set()

        interests_lower = interests.lower() if interests else ''

        rules = [
            ({'tech', 'computer', 'code', 'coding', 'program', 'software', 'it', 'data', 'cloud'},
             ['Software Engineer', 'Data Scientist', 'Cloud Architect', 'Cybersecurity Analyst', 'Full Stack Developer'],
             ['BTech in Computer Science', 'BCA', 'BSc IT', 'Diploma in Web Dev']),

            ({'business', 'manage', 'market', 'sell', 'trade', 'startup', 'hr', 'finance'},
             ['HR Manager', 'Sales Executive', 'Business Analyst', 'Marketing Director'],
             ['BBA', 'MBA', 'BCom', 'Economics']),

            ({'science', 'bio', 'health', 'medic', 'doctor'},
             ['Doctor', 'Pharmacist', 'Researcher'],
             ['MBBS', 'BSc Biology', 'BPharma']),

            ({'art', 'design', 'creative', 'ui', 'ux'},
             ['UI/UX Designer', 'Graphic Designer'],
             ['BDes', 'Fine Arts']),

            ({'law', 'legal'},
             ['Lawyer', 'Judge'],
             ['LLB', 'LLM'])
        ]

        for keywords, careers, courses in rules:
            if any(kw in interests_lower for kw in keywords):
                recommended_careers.update(careers)
                recommended_courses.update(courses)

        if not recommended_careers:
            recommended_careers.update(['General Jobs'])
            recommended_courses.update(['Any Degree'])

        student = Student(
            name=name,
            education_level=education_level,
            interests=interests,
            location=location
        )

        db.session.add(student)
        db.session.commit()

        return render_template(
            'recommend.html',
            careers=list(recommended_careers),
            courses=list(recommended_courses),
            name=name
        )

    return render_template('recommend.html')


# ✅ Required for local run (safe for Render too)
if __name__ == '__main__':
    app.run(debug=True)