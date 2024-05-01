import os
import boto3
import json
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import psycopg2


load_dotenv()

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        return conn
    except (Exception, psycopg2.Error) as error:
        print("Error connecting to the database:", error)
        print("Database connection details:")
        print(f"Host: {Config.DB_HOST}")
        print(f"Port: {Config.DB_PORT}")
        print(f"Database: {Config.DB_NAME}")
        print(f"User: {Config.DB_USER}")
        print(f'Password: {Config.DB_PASSWORD}')
        return None

def get_secret():
    secret_name = os.environ.get('AWS_SECRET_NAME')
    region_name = "us-east-2"

    # Create a Secrets Manager client
    client = boto3.client('secretsmanager', region_name=region_name)
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret_string = get_secret_value_response['SecretString']
    secret_data =  json.loads(secret_string)
    db_password = secret_data['password']
    return db_password


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    FIREBASE_CONFIG = {
        'apiKey': os.environ.get('FIREBASE_API_KEY'),
        'authDomain': os.environ.get('FIREBASE_AUTH_DOMAIN'),
        'projectId': os.environ.get('FIREBASE_PROJECT_ID'),
        'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET'),
        'messagingSenderId': os.environ.get('FIREBASE_MESSAGING_SENDER_ID'),
        'appId': os.environ.get('FIREBASE_APP_ID'),
        'measurementId': os.environ.get('FIREBASE_MEASUREMENT_ID'),
        'databaseURL': os.environ.get('FIREBATE_DATABASE_URL')
    }
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('DB_PORT')
    DB_NAME = os.environ.get('DB_NAME')
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = get_secret()
    SQLALCHEMY_DATABASE_URI = f'postgresql://{os.environ.get("DB_USER")}:{DB_PASSWORD}@{os.environ.get("DB_HOST")}:{os.environ.get("DB_PORT")}/{os.environ.get("DB_NAME")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

Config()