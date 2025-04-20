import os
from flask import render_template, url_for, flash, redirect, request, jsonify, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from datetime import datetime

from app import app, db
from models import User, Resume, Template
from forms import (
    RegistrationForm, LoginForm, ResumeForm, TemplateUploadForm,
    KeywordOptimizationForm, PolishResumeForm, GenerateSummaryForm
)
from ai_services import (
    generate_resume_suggestions, polish_resume, calculate_ats_score,
    optimize_keywords, generate_resume_summary
)
from utils import (
    allowed_file, save_template_file, check_premium_access,
    format_ats_score, get_premium_payment_link, get_premium_amount
)

# Load configuration
from config import Config
for key, value in vars(Config).items():
    if not key.startswith('__'):
        app.config[key] = value

# Create uploads folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# ----------------- Authentication Routes -----------------

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('home.html', title='Resume Builder')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('login.html', title='Login', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Account created for {form.username.data}! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html', title='Sign Up', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# ----------------- Dashboard Route -----------------

@app.route('/dashboard')
@login_required
def dashboard():
    resumes = Resume.query.filter_by(user_id=current_user.id).all()
    templates = Template.query.filter_by(user_id=current_user.id).all()
    
    return render_template(
        'dashboard.html', 
        title='Dashboard',
        resumes=resumes,
        templates=templates,
        is_premium=current_user.is_premium,
        premium_payment_link=get_premium_payment_link(),
        premium_amount=get_premium_amount()
    )

# ----------------- Resume Routes -----------------

@app.route('/resume/chatbot', methods=['GET', 'POST'])
@login_required
def chatbot_resume():
    """AI chatbot-based resume creation route."""
    templates = Template.query.filter_by(user_id=current_user.id).all()
    
    return render_template(
        'chatbot_resume.html',
        title='AI Resume Builder',
        templates=templates,
        is_premium=current_user.is_premium,
        premium_payment_link=get_premium_payment_link()
    )

@app.route('/resume/save-chatbot', methods=['POST'])
@login_required
def save_chatbot_resume():
    """Save a resume created from the chatbot interface."""
    data = request.json
    
    if not data or 'resumeData' not in data:
        return jsonify({'success': False, 'error': 'Missing resume data'}), 400
    
    try:
        resume_data = data['resumeData']
        
        # Create a formatted title based on user's name and date
        title = f"{resume_data.get('full_name', 'My Resume')} - {datetime.now().strftime('%B %d, %Y')}"
        
        # Format the resume content
        content = generate_formatted_resume_content(resume_data)
        
        # Get template ID if applicable
        template_id = data.get('templateId')
        
        # Create new Resume object
        new_resume = Resume(
            title=title,
            content=content,
            user_id=current_user.id,
            template_id=template_id if template_id else None
        )
        
        # Add to database
        db.session.add(new_resume)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'resume_id': new_resume.id,
            'message': 'Resume saved successfully!'
        })
    
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error saving chatbot resume: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def generate_formatted_resume_content(data):
    """Format resume data from chatbot into a structured content string."""
    content = []
    
    # Add name as heading
    content.append(f"# {data.get('full_name', 'Your Name')}")
    
    # Add contact info
    if data.get('contact'):
        content.append(data['contact'])
    
    # Add professional summary
    if data.get('objective') and data['objective'].lower() != 'skip':
        content.append("\n## PROFESSIONAL SUMMARY")
        content.append(data['objective'])
    
    # Add education
    if data.get('education'):
        content.append("\n## EDUCATION")
        for item in data['education'].split(';'):
            if item.strip():
                content.append(f"- {item.strip()}")
    
    # Add experience
    if data.get('experience') and data['experience'].lower() != 'skip':
        content.append("\n## EXPERIENCE")
        for item in data['experience'].split(';'):
            if item.strip():
                content.append(f"- {item.strip()}")
    
    # Add projects
    if data.get('projects') and data['projects'].lower() != 'skip':
        content.append("\n## PROJECTS")
        for item in data['projects'].split(';'):
            if item.strip():
                content.append(f"- {item.strip()}")
    
    # Add skills
    if data.get('skills'):
        content.append("\n## SKILLS")
        content.append(data['skills'])
    
    # Add certifications
    if data.get('certifications') and data['certifications'].lower() != 'skip':
        content.append("\n## CERTIFICATIONS")
        for item in data['certifications'].split(';'):
            if item.strip():
                content.append(f"- {item.strip()}")
    
    # Add achievements
    if data.get('achievements') and data['achievements'].lower() != 'skip':
        content.append("\n## ACHIEVEMENTS")
        for item in data['achievements'].split(';'):
            if item.strip():
                content.append(f"- {item.strip()}")
    
    # Add languages
    if data.get('languages') and data['languages'].lower() != 'skip':
        content.append("\n## LANGUAGES")
        content.append(data['languages'])
    
    return "\n".join(content)

@app.route('/resume/new', methods=['GET', 'POST'])
@login_required
def new_resume():
    form = ResumeForm()
    templates = Template.query.filter_by(user_id=current_user.id).all()
    
    if form.validate_on_submit():
        resume = Resume(
            title=form.title.data,
            content=form.content.data,
            job_description=form.job_description.data,
            user_id=current_user.id
        )
        
        if form.template_id.data:
            resume.template_id = form.template_id.data
        
        db.session.add(resume)
        db.session.commit()
        
        flash('Your resume has been created!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template(
        'resume_builder.html', 
        title='Create Resume',
        form=form,
        templates=templates,
        is_premium=current_user.is_premium,
        premium_payment_link=get_premium_payment_link()
    )

@app.route('/resume/<int:resume_id>', methods=['GET', 'POST'])
@login_required
def view_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    
    # Check if the resume belongs to the current user
    if resume.user_id != current_user.id:
        abort(403)  # Forbidden
    
    form = ResumeForm()
    templates = Template.query.filter_by(user_id=current_user.id).all()
    
    if form.validate_on_submit():
        resume.title = form.title.data
        resume.content = form.content.data
        resume.job_description = form.job_description.data
        
        if form.template_id.data:
            resume.template_id = form.template_id.data
            
        resume.date_updated = datetime.utcnow()
        
        db.session.commit()
        flash('Your resume has been updated!', 'success')
        return redirect(url_for('dashboard'))
    
    # Fill form with existing data
    if request.method == 'GET':
        form.title.data = resume.title
        form.content.data = resume.content
        form.job_description.data = resume.job_description
        form.template_id.data = resume.template_id
    
    return render_template(
        'resume_builder.html', 
        title='Edit Resume',
        form=form,
        resume=resume,
        templates=templates,
        is_premium=current_user.is_premium,
        premium_payment_link=get_premium_payment_link()
    )

@app.route('/resume/<int:resume_id>/delete', methods=['POST'])
@login_required
def delete_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    
    # Check if the resume belongs to the current user
    if resume.user_id != current_user.id:
        abort(403)  # Forbidden
    
    db.session.delete(resume)
    db.session.commit()
    
    flash('Your resume has been deleted!', 'success')
    return redirect(url_for('dashboard'))

# ----------------- Template Routes -----------------

@app.route('/template/upload', methods=['GET', 'POST'])
@login_required
def upload_template():
    # Check if user has premium access
    if not current_user.is_premium:
        return redirect(url_for('premium_required', feature='template_upload'))
    
    form = TemplateUploadForm()
    
    if form.validate_on_submit():
        if form.file.data and allowed_file(form.file.data.filename):
            content = save_template_file(form.file.data)
            
            if content:
                template = Template(
                    name=form.name.data,
                    content=content,
                    user_id=current_user.id
                )
                
                db.session.add(template)
                db.session.commit()
                
                flash('Your template has been uploaded!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Error saving template file.', 'danger')
        else:
            flash('Invalid file format. Only HTML files are allowed.', 'danger')
    
    return render_template(
        'template_upload.html', 
        title='Upload Template',
        form=form
    )

@app.route('/template/<int:template_id>/delete', methods=['POST'])
@login_required
def delete_template(template_id):
    template = Template.query.get_or_404(template_id)
    
    # Check if the template belongs to the current user
    if template.user_id != current_user.id:
        abort(403)  # Forbidden
    
    db.session.delete(template)
    db.session.commit()
    
    flash('Your template has been deleted!', 'success')
    return redirect(url_for('dashboard'))

# ----------------- AI Feature Routes -----------------

@app.route('/resume/ai-suggestions', methods=['POST'])
@login_required
def ai_suggestions():
    # Check if user has premium access
    if not current_user.is_premium:
        return jsonify({'error': 'Premium access required for this feature'})
    
    data = request.json
    job_description = data.get('job_description', '')
    resume_content = data.get('resume_content', '')
    
    suggestions = generate_resume_suggestions(job_description, resume_content)
    
    return jsonify(suggestions)

@app.route('/resume/<int:resume_id>/polish', methods=['GET', 'POST'])
@login_required
def polish_resume_route(resume_id):
    # Check if user has premium access
    if not current_user.is_premium:
        return redirect(url_for('premium_required', feature='polish_resume'))
    
    resume = Resume.query.get_or_404(resume_id)
    
    # Check if the resume belongs to the current user
    if resume.user_id != current_user.id:
        abort(403)  # Forbidden
    
    form = PolishResumeForm()
    
    if form.validate_on_submit():
        polished_content = polish_resume(form.content.data)
        
        if polished_content:
            resume.content = polished_content
            resume.date_updated = datetime.utcnow()
            
            db.session.commit()
            flash('Your resume has been polished!', 'success')
            return redirect(url_for('view_resume', resume_id=resume.id))
        else:
            flash('Error polishing resume. Please try again.', 'danger')
    
    if request.method == 'GET':
        form.resume_id.data = resume.id
        form.content.data = resume.content
    
    return render_template(
        'polish_resume.html', 
        title='Polish Resume',
        form=form,
        resume=resume
    )

@app.route('/resume/<int:resume_id>/ats-score', methods=['GET'])
@login_required
def ats_score(resume_id):
    # Check if user has premium access
    if not current_user.is_premium:
        return redirect(url_for('premium_required', feature='ats_score'))
    
    resume = Resume.query.get_or_404(resume_id)
    
    # Check if the resume belongs to the current user
    if resume.user_id != current_user.id:
        abort(403)  # Forbidden
    
    if request.method == 'GET':
        # Calculate ATS score if not already calculated or if explicitly requested
        if resume.ats_score == 0 or request.args.get('recalculate', False):
            score_data = calculate_ats_score(resume.content, resume.job_description)
            
            if score_data and 'score' in score_data:
                resume.ats_score = score_data['score']
                db.session.commit()
            else:
                flash('Error calculating ATS score. Please try again.', 'danger')
        else:
            # Retrieve previously calculated score
            score_data = calculate_ats_score(resume.content, resume.job_description)
        
        formatted_score = format_ats_score(score_data)
        
        return render_template(
            'ats_score.html', 
            title='ATS Score',
            resume=resume,
            score_data=formatted_score
        )

@app.route('/resume/<int:resume_id>/keyword-optimization', methods=['GET', 'POST'])
@login_required
def keyword_optimization(resume_id):
    # Check if user has premium access
    if not current_user.is_premium:
        return redirect(url_for('premium_required', feature='keyword_optimization'))
    
    resume = Resume.query.get_or_404(resume_id)
    
    # Check if the resume belongs to the current user
    if resume.user_id != current_user.id:
        abort(403)  # Forbidden
    
    form = KeywordOptimizationForm()
    
    if form.validate_on_submit():
        optimization_data = optimize_keywords(resume.content, form.job_description.data)
        
        if optimization_data and 'optimized_resume' in optimization_data:
            resume.content = optimization_data['optimized_resume']
            resume.job_description = form.job_description.data
            resume.date_updated = datetime.utcnow()
            
            db.session.commit()
            flash('Your resume has been optimized for keywords!', 'success')
            return redirect(url_for('view_resume', resume_id=resume.id))
        else:
            flash('Error optimizing keywords. Please try again.', 'danger')
    
    if request.method == 'GET':
        form.resume_id.data = resume.id
        if resume.job_description:
            form.job_description.data = resume.job_description
    
    return render_template(
        'keyword_optimization.html', 
        title='Keyword Optimization',
        form=form,
        resume=resume
    )

@app.route('/resume/<int:resume_id>/generate-summary', methods=['GET', 'POST'])
@login_required
def generate_summary(resume_id):
    # Check if user has premium access
    if not current_user.is_premium:
        return redirect(url_for('premium_required', feature='generate_summary'))
    
    resume = Resume.query.get_or_404(resume_id)
    
    # Check if the resume belongs to the current user
    if resume.user_id != current_user.id:
        abort(403)  # Forbidden
    
    form = GenerateSummaryForm()
    
    if form.validate_on_submit():
        summary = generate_resume_summary(form.content.data)
        
        if summary:
            resume.summary = summary
            db.session.commit()
            
            return render_template(
                'resume_summary.html', 
                title='Resume Summary',
                resume=resume,
                summary=summary
            )
        else:
            flash('Error generating summary. Please try again.', 'danger')
            return redirect(url_for('generate_summary', resume_id=resume.id))
    
    if request.method == 'GET':
        form.resume_id.data = resume.id
        form.content.data = resume.content
    
    return render_template(
        'resume_summary.html', 
        title='Generate Summary',
        form=form,
        resume=resume,
        summary=resume.summary
    )

# ----------------- Premium Route -----------------

@app.route('/premium/activate', methods=['POST'])
@login_required
def activate_premium():
    # In a real app, this would verify the payment status from Razorpay
    # For this demonstration, we'll simply update the user's status
    current_user.is_premium = True
    db.session.commit()
    
    flash('Premium access activated! You now have access to all premium features.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/premium/required/<feature>')
@login_required
def premium_required(feature):
    return render_template(
        'premium_required.html', 
        title='Premium Required',
        feature=feature,
        payment_link=get_premium_payment_link(),
        premium_amount=get_premium_amount()
    )

# ----------------- Error Handlers -----------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
