"""
Lambda function to register a new user
"""
import json
import uuid
import os
import sys

# Add lambda-functions directory to path
sys.path.append(os.path.dirname(__file__))

from db_utils import create_user, get_user_by_email
from auth_utils import hash_password


def lambda_handler(event, context):
    """
    Register a new user
    
    Expected event body:
    {
        "email": "user@example.com",
        "password": "securepassword",
        "firstName": "John",  // optional
        "lastName": "Doe"      // optional
    }
    
    Returns:
    {
        "statusCode": 201,
        "body": {
            "message": "User created successfully",
            "userId": "uuid"
        }
    }
    """
    try:
        body = event.get('body', {})
        
        if isinstance(body, str):
            body = json.loads(body)   

        email = body.get('email')
        password = body.get('password')
        first_name = body.get('firstName')
        last_name = body.get('lastName')
        
        # Validate required fields
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Email and password are required'
                })
            }
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Invalid email format'
                })
            }
        
        # Validate password strength
        if len(password) < 8:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Password must be at least 8 characters long'
                })
            }
        
        # Check if user already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            return {
                'statusCode': 409,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'User with this email already exists'
                })
            }
        
        user_id = str(uuid.uuid4())
        password_hash = hash_password(password)
        
        # Create user in DynamoDB
        success = create_user(
            user_id=user_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=password_hash,
        )
        
        if not success:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Failed to create user'
                })
            }
        
        # Return success response
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'User created successfully',
                'userId': user_id
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            })
        }
