import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get("SESSION_SECRET", "fallback-secret-key-for-development")
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///resume_builder.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI API configuration
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
    ALLOWED_EXTENSIONS = {'html', 'txt', 'pdf', 'docx'}
    
    # Razorpay payment link
    RAZORPAY_PAYMENT_LINK = "https://razorpay.me/@resume12"
    
    # Premium amount
    PREMIUM_AMOUNT = "₹99"
