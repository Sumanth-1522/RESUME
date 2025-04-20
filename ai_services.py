import os
import json
import logging
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

logger = logging.getLogger(__name__)

def generate_resume_suggestions(job_description, current_resume=None):
    """Generate AI suggestions for resume content based on job description"""
    try:
        prompt = f"""
        As an AI resume writing assistant, please provide suggestions to improve this resume for the following job description:
        
        JOB DESCRIPTION:
        {job_description}
        
        {'CURRENT RESUME:' + current_resume if current_resume else 'Please generate a structure for a professional resume based on the job description.'}
        
        Provide suggestions for improving or creating each section of the resume, focusing on:
        1. Skills that match the job description
        2. Experience highlights that should be emphasized
        3. Educational qualifications to highlight
        4. Achievements that would stand out
        
        Return your response as a JSON object with the following structure:
        {{
            "skills": ["skill 1", "skill 2", ...],
            "experience": ["suggestion 1", "suggestion 2", ...],
            "education": ["suggestion 1", "suggestion 2", ...],
            "achievements": ["suggestion 1", "suggestion 2", ...],
            "overall_suggestions": "General advice for the resume"
        }}
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    except Exception as e:
        logger.error(f"Error generating resume suggestions: {str(e)}")
        return {
            "error": "Failed to generate resume suggestions",
            "details": str(e)
        }

def polish_resume(resume_content):
    """Improve grammar and formatting of resume"""
    try:
        prompt = f"""
        As an expert resume editor, please improve the grammar, formatting, and professional tone of the following resume:
        
        {resume_content}
        
        Focus on:
        1. Fixing any grammatical errors
        2. Improving sentence structure
        3. Using strong action verbs
        4. Maintaining consistent formatting
        5. Enhancing professional language
        
        Return only the improved resume text without explanations.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        logger.error(f"Error polishing resume: {str(e)}")
        return None

def calculate_ats_score(resume_content, job_description=None):
    """Calculate ATS score for a resume against an optional job description"""
    try:
        prompt = f"""
        As an ATS (Applicant Tracking System) analyzer, evaluate the following resume 
        {f'for this job description: {job_description}' if job_description else 'for general ATS compatibility'}
        
        RESUME:
        {resume_content}
        
        Analyze the resume and provide:
        1. An ATS compatibility score from 0-100
        2. Detailed feedback on what improves or reduces the score
        3. Missing keywords or qualifications
        4. Formatting issues that might affect ATS scanning
        5. Specific recommendations for improvement
        
        Format your response as a JSON object with the following structure:
        {{
            "score": 85,
            "strengths": ["strength 1", "strength 2", ...],
            "weaknesses": ["weakness 1", "weakness 2", ...],
            "missing_keywords": ["keyword 1", "keyword 2", ...],
            "formatting_issues": ["issue 1", "issue 2", ...],
            "recommendations": ["recommendation 1", "recommendation 2", ...]
        }}
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    except Exception as e:
        logger.error(f"Error calculating ATS score: {str(e)}")
        return {
            "score": 0,
            "error": "Failed to calculate ATS score",
            "details": str(e)
        }

def optimize_keywords(resume_content, job_description):
    """Optimize resume keywords based on job description"""
    try:
        prompt = f"""
        As a keyword optimization expert for resumes, analyze the following resume and job description:
        
        RESUME:
        {resume_content}
        
        JOB DESCRIPTION:
        {job_description}
        
        Please provide:
        1. A list of important keywords from the job description that are missing in the resume
        2. Suggestions for where and how to incorporate these keywords naturally
        3. A revised version of the resume that incorporates these keywords appropriately
        
        Format your response as a JSON object with the following structure:
        {{
            "missing_keywords": ["keyword 1", "keyword 2", ...],
            "placement_suggestions": ["suggestion 1", "suggestion 2", ...],
            "optimized_resume": "The full text of the optimized resume"
        }}
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    except Exception as e:
        logger.error(f"Error optimizing keywords: {str(e)}")
        return {
            "error": "Failed to optimize keywords",
            "details": str(e)
        }

def generate_resume_summary(resume_content):
    """Generate a professional summary for a resume"""
    try:
        prompt = f"""
        As a professional resume writer, generate a compelling professional summary based on the following resume content:
        
        {resume_content}
        
        Create a concise, powerful professional summary (3-5 sentences) that:
        1. Highlights key qualifications and experience
        2. Incorporates relevant skills and achievements
        3. Presents a strong value proposition to employers
        4. Uses industry-appropriate language
        
        The summary should be specific, quantifiable when possible, and tailored to the candidate's career level and industry.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        logger.error(f"Error generating resume summary: {str(e)}")
        return None
        
def process_chatbot_resume(user_data, template_id=None):
    """Process the data collected from the chatbot to create a resume"""
    try:
        # Organize the user data
        full_name = user_data.get('full_name', '')
        contact = user_data.get('contact', '')
        education = user_data.get('education', '')
        experience = user_data.get('experience', '')
        projects = user_data.get('projects', '')
        skills = user_data.get('skills', '')
        certifications = user_data.get('certifications', '')
        objective = user_data.get('objective', '')
        achievements = user_data.get('achievements', '')
        languages = user_data.get('languages', '')
        
        # Generate professional content using OpenAI
        prompt = f"""
        Create a professional resume using the following information:
        
        Name: {full_name}
        Contact: {contact}
        
        Education: {education if education and education.lower() != 'skip' else 'N/A'}
        
        Experience: {experience if experience and experience.lower() != 'skip' else 'N/A'}
        
        Projects: {projects if projects and projects.lower() != 'skip' else 'N/A'}
        
        Skills: {skills}
        
        Certifications: {certifications if certifications and certifications.lower() != 'skip' else 'N/A'}
        
        Career Objective: {objective if objective and objective.lower() != 'skip' else 'N/A'}
        
        Achievements: {achievements if achievements and achievements.lower() != 'skip' else 'N/A'}
        
        Languages: {languages if languages and languages.lower() != 'skip' else 'N/A'}
        
        Format the resume professionally with clear sections and bullet points. 
        Skip any sections marked as N/A entirely (don't include them). Make sure to emphasize achievements and responsibilities.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional resume writing assistant. Create well-structured, professional resumes."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        
        resume_content = response.choices[0].message.content.strip()
        
        # Calculate ATS score if requested
        ats_score = 0
        if user_data.get('calculate_ats', False):
            ats_data = calculate_ats_score(resume_content)
            if ats_data and 'score' in ats_data:
                ats_score = ats_data['score']
        
        # Return the generated content and other metadata
        return {
            "title": f"{full_name}'s Resume",
            "content": resume_content,
            "ats_score": ats_score
        }
        
    except Exception as e:
        logger.error(f"Error processing chatbot resume: {e}")
        return None

def calculate_ats_compatibility(resume_content, job_description=None):
    """Calculate ATS compatibility score and provide recommendations for the chatbot interface"""
    try:
        prompt = f"""
        Analyze this resume for ATS (Applicant Tracking System) compatibility:
        
        {resume_content}
        
        {f"For this job description: {job_description}" if job_description else ""}
        
        Provide a JSON response with:
        1. An overall score from 0-100
        2. A list of strengths (what's good about the resume for ATS)
        3. A list of weaknesses (what could be improved for ATS)
        4. A list of specific recommendations
        
        Format the response as valid JSON like this:
        {{
            "score": 85,
            "strengths": ["Good use of keywords", "Clear section headings"],
            "weaknesses": ["Missing quantifiable achievements", "Too much formatting"],
            "recommendations": ["Add more industry-specific keywords", "Use bullet points for better readability"]
        }}
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an ATS analysis expert. Provide detailed ATS compatibility analysis for resumes."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the JSON response
        result = json.loads(response.choices[0].message.content)
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculating ATS compatibility: {e}")
        return {"score": 0, "strengths": [], "weaknesses": [], "recommendations": []}

def save_chatbot_resume(user_id, resume_data, template_id=None):
    """Save a resume created from the chatbot to the database"""
    from app import db
    from models import Resume
    from datetime import datetime
    
    try:
        # Create a new resume record
        new_resume = Resume(
            title=resume_data.get('title', 'My Resume'),
            content=resume_data.get('content', ''),
            ats_score=resume_data.get('ats_score', 0),
            user_id=user_id,
            template_id=template_id,
            date_created=datetime.utcnow(),
            date_updated=datetime.utcnow()
        )
        
        # Save to database
        db.session.add(new_resume)
        db.session.commit()
        
        return new_resume.id
    except Exception as e:
        logger.error(f"Error saving chatbot resume: {e}")
        db.session.rollback()
        return None
