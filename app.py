from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Student, College, Job
from datetime import datetime, timedelta
import os

app = Flask(__name__)
# Use an absolute path for SQLite to avoid issues
basedir = os.path.abspath(os.path.dirname(__name__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super_secret_key' # for flash messages

db.init_app(app)

#with app.app_context():
    #db.create_all()

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
    # Assume Jobs that have last_date > now are active, and last_date is upcoming
    
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
             job.status = 'Active' # No last date means always active
             
        if timeframe == 'active' and job.status != 'Active': continue
        if timeframe == 'upcoming' and job.status != 'Upcoming': continue
        
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

        # Enhanced rule-based recommendations
        recommended_careers = set()
        recommended_courses = set()
        
        interests_lower = interests.lower() if interests else ''
        
        rules = [
            ({'tech', 'computer', 'code', 'coding', 'program', 'software', 'it', 'data', 'cloud'}, 
             ['Software Engineer', 'Data Scientist', 'Cloud Architect', 'Cybersecurity Analyst', 'Full Stack Developer'], 
             ['BTech in Computer Science', 'BCA', 'BSc in Information Technology', 'Diploma in Web Development']),
             
            ({'business', 'manage', 'market', 'sell', 'trade', 'startup', 'hr', 'finance', 'economy'}, 
             ['HR Manager', 'Sales Executive', 'Business Analyst', 'Marketing Director', 'Financial Planner, Entrepreneur'], 
             ['BBA', 'MBA', 'BCom', 'BA in Economics', 'CA Foundation']),
             
            ({'science', 'bio', 'health', 'medic', 'doctor', 'care', 'life', 'pharm'}, 
             ['Clinical Researcher', 'Pharmacist', 'Medical Officer', 'Lab Technician', 'Surgeon'], 
             ['MBBS', 'BSc in Biology', 'BPharma', 'Nursing', 'BDS']),
             
            ({'art', 'design', 'draw', 'creative', 'paint', 'ui', 'ux', 'graphic'}, 
             ['UI/UX Designer', 'Graphic Designer', 'Animator', 'Art Director', 'Product Designer'], 
             ['BDes', 'BA in Fine Arts', 'Diploma in Graphic Design']),
             
            ({'law', 'legal', 'justice', 'court', 'crime', 'advocate'}, 
             ['Corporate Lawyer', 'Legal Advisor', 'Judge', 'Criminal Defense Attorney'], 
             ['LLB', 'BA LLB', 'LLM']),
             
            ({'build', 'civil', 'construct', 'archit', 'space', 'plan'}, 
             ['Civil Engineer', 'Architect', 'Urban Planner', 'Structural Engineer'], 
             ['BTech in Civil', 'BArch', 'Diploma in Civil Engineering']),
             
            ({'educat', 'teach', 'school', 'student', 'learn', 'professor'}, 
             ['Teacher', 'University Professor', 'Educational Counselor', 'Curriculum Developer'], 
             ['BEd', 'BA in Education', 'MA/MSc in Core Subject']),
             
            ({'govn', 'public', 'social', 'society', 'ssc', 'upsc', 'admin'},
             ['Civil Servant (IAS/IPS)', 'Government Clerk', 'Public Policy Analyst', 'Diplomat'],
             ['BA General', 'MA in Political Science', 'BSc'])
        ]
        
        for keywords, careers, courses in rules:
            if any(kw in interests_lower for kw in keywords):
                recommended_careers.update(careers)
                recommended_courses.update(courses)
                
        if not recommended_careers:
            recommended_careers.update(['General Operations', 'Customer Success Associate', 'Administrative Assistant'])
            recommended_courses.update(['BA General', 'BCom', 'Any degree program'])

        recommended_careers = list(recommended_careers)[:6] # Limit to top 6 best matches
        recommended_courses = list(recommended_courses)[:6]

        # Save student profile
        student = Student(name=name, education_level=education_level, interests=interests, location=location)
        db.session.add(student)
        db.session.commit()
        
        return render_template('recommend.html', 
                               careers=recommended_careers, 
                               courses=recommended_courses,
                               name=name)

    return render_template('recommend.html')

if __name__ == '__main__':
    app.run(debug=True)
