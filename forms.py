from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose a different one.')
            
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please use a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class ResumeForm(FlaskForm):
    title = StringField('Resume Title', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Resume Content', validators=[DataRequired()])
    job_description = TextAreaField('Job Description (Optional)')
    template_id = HiddenField('Template ID')
    submit = SubmitField('Save Resume')
    
    # Fields for structured resume entry
    full_name = StringField('Full Name')
    contact_info = StringField('Contact Information (Email, Phone, LinkedIn)')
    summary = TextAreaField('Professional Summary')
    education = TextAreaField('Education (Degree, School, Year)')
    experience = TextAreaField('Work Experience')
    skills = TextAreaField('Skills')
    certifications = TextAreaField('Certifications')
    achievements = TextAreaField('Achievements')
    languages = TextAreaField('Languages')
    use_structured_form = HiddenField('Use Structured Form')


class TemplateUploadForm(FlaskForm):
    name = StringField('Template Name', validators=[DataRequired(), Length(max=100)])
    file = FileField('Template File', validators=[
        DataRequired(),
        FileAllowed(['html'], 'HTML files only!')
    ])
    submit = SubmitField('Upload Template')


class KeywordOptimizationForm(FlaskForm):
    resume_id = HiddenField('Resume ID', validators=[DataRequired()])
    job_description = TextAreaField('Job Description', validators=[DataRequired()])
    submit = SubmitField('Optimize')


class PolishResumeForm(FlaskForm):
    resume_id = HiddenField('Resume ID', validators=[DataRequired()])
    content = TextAreaField('Resume Content', validators=[DataRequired()])
    submit = SubmitField('Polish')


class GenerateSummaryForm(FlaskForm):
    resume_id = HiddenField('Resume ID', validators=[DataRequired()])
    content = TextAreaField('Resume Content', validators=[DataRequired()])
    submit = SubmitField('Generate Summary')
