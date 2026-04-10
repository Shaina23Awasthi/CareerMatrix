from app import app, db
from models import College, Job
from datetime import datetime, timedelta
import random

def seed_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        now = datetime.now()
        
        locations = ['Bangalore', 'Chandigarh', 'Chennai', 'Hyderabad', 'Pune', 'Mumbai', 'New Delhi', 'Kolkata', 'Ahmedabad', 'Jaipur', 'Lucknow', 'Noida']
        courses = ['BTech', 'BSc', 'BCA', 'BBA', 'BCom', 'BA', 'MBBS', 'BArch', 'LLB', 'BEd', 'BDes', 'BPharma']
        educations = ['10th', '12th', 'Diploma', 'Graduate', 'BTech/BE', 'BSc/BCA', 'BCom/BBA', 'BA', 'Postgraduate', 'MTech/ME', 'MBA/MCA', 'PhD']
        job_types = ['Private', 'Government']
        
        college_list = []
        job_list = []

        # Generate colleges for every combinations
        for loc in locations:
            for course in courses:
                colleges_to_create = random.randint(1, 3) # 1 to 3 colleges per course per city
                for i in range(colleges_to_create):
                    c = College(
                        name=f"{loc} Institute of {course} Studies" if i == 0 else (f"{loc} National University" if i == 1 else f"Royal College of {loc}"),
                        location=loc,
                        course=course,
                        fees=random.randint(30000, 300000),
                        rating=round(random.uniform(3.5, 5.0), 1),
                        contact_info=f"admin@{loc.lower().replace(' ', '')}edu.in",
                        registration_link=f"https://{loc.lower().replace(' ', '')}edu.in/apply"
                    )
                    college_list.append(c)

        # Generate jobs for every location and education level
        # Also include "All India"
        job_locations = locations + ['All India']
        
        for loc in job_locations:
            for edu in educations:
                jobs_to_create = random.randint(2, 4) # 2 to 4 jobs per education per city
                for i in range(jobs_to_create):
                    j_type = random.choice(job_types)
                    days_offset = random.randint(-15, 60) # Some expired, some upcoming, some active
                    
                    is_gov = j_type == 'Government'
                    title = f"Specialist {edu} Role" if not is_gov else f"Govt Officer Grade ({edu})"
                    if edu in ['BTech/BE', 'BSc/BCA', 'MTech/ME']: title = "Software/IT Engineer"
                    elif edu in ['BCom/BBA', 'MBA/MCA']: title = "Financial/Management Analyst"
                    elif edu in ['MBBS', 'BPharma']: title = "Medical/Healthcare Staff"
                    
                    j = Job(
                        title=title,
                        organization=f"Federal {loc} Dept" if is_gov else f"{loc} Tech/Business Solutions",
                        location=loc,
                        education_required=edu,
                        job_type=j_type,
                        salary_range=f"{random.randint(3, 15)} LPA",
                        last_date=now + timedelta(days=days_offset),
                        application_link=f"https://{loc.lower().replace(' ', '')}jobs.com/apply"
                    )
                    job_list.append(j)

        db.session.bulk_save_objects(college_list)
        db.session.bulk_save_objects(job_list)
        db.session.commit()
        print(f"Massive fake data seeded! {len(college_list)} colleges and {len(job_list)} jobs created.")

if __name__ == '__main__':
    seed_data()
