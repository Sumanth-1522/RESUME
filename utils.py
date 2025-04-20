import os
import logging
from werkzeug.utils import secure_filename
from flask import current_app
from models import User

logger = logging.getLogger(__name__)

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_template_file(file):
    """Save a template file to the uploads directory"""
    try:
        if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
            os.makedirs(current_app.config['UPLOAD_FOLDER'])
            
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Read the file content
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Delete the temporary file as we've stored the content in the database
        os.remove(file_path)
        
        return content
    except Exception as e:
        logger.error(f"Error saving template file: {str(e)}")
        return None

def check_premium_access(user):
    """Check if a user has premium access"""
    if not user:
        return False
    return user.is_premium

def format_ats_score(score_data):
    """Format ATS score data for display"""
    if not score_data or 'score' not in score_data:
        return {
            'score': 0,
            'strengths': [],
            'weaknesses': [],
            'missing_keywords': [],
            'formatting_issues': [],
            'recommendations': []
        }
    
    # Ensure all expected keys are present
    formatted_data = {
        'score': score_data.get('score', 0),
        'strengths': score_data.get('strengths', []),
        'weaknesses': score_data.get('weaknesses', []),
        'missing_keywords': score_data.get('missing_keywords', []),
        'formatting_issues': score_data.get('formatting_issues', []),
        'recommendations': score_data.get('recommendations', [])
    }
    
    return formatted_data

def get_premium_payment_link():
    """Get the Razorpay payment link"""
    return current_app.config['RAZORPAY_PAYMENT_LINK']

def get_premium_amount():
    """Get the premium amount"""
    return current_app.config['PREMIUM_AMOUNT']
