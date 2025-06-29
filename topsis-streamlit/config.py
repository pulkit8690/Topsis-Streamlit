import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://db_user:db_pass@localhost:5432/db_name')
    SQLALCHEMY_TRACK_MODIFICATIONS = False