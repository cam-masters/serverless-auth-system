"""
Lambda function to authenticate a user and return OAuth 2.0 token
"""
import json
import os
import sys
from datetime import datetime

# Add lambda-functions directory to path
sys.path.append(os.path.dirname(__file__))

from db_utils import get_user_by_email
from auth_utils import verify_password, generate_access_token, create_oauth_response


def lambda_handler(event, context):
    """
    Authenticate a user and return an OAuth 2.0 access token
    
    Expected event body:
    {
        "email": "user@example.com",
        "password": "securepassword"
    }
    
    Returns:
    {
        "statusCode": 200,
        "body": {
            "access_token": "jwt_token_here",
            "token_type": "Bearer",
            "expires_in": 86400,
            "scope": "read write"
        }
    }
    """
    try:
        # When called from API Gateway, event['body'] is a JSON string
        body = event.get('body', {})
        
        if isinstance(body, str):
            body = json.loads(body)

        email = body.get('email')
        password = body.get('password')
        
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
        
        # Get user from database
        user = get_user_by_email(email)
        
        if not user:
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Invalid credentials'
                })
            }
        
        # Verify password
        password_hash = user.get('passwordHash')
        if not verify_password(password, password_hash):
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Invalid credentials'
                })
            }
        
        # Generate access token
        user_id = user.get('userId')
        access_token = generate_access_token(user_id, email)
        
        # Create OAuth 2.0 compliant response
        oauth_response = create_oauth_response(access_token)
        
        oauth_response['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'no-store',
                'Pragma': 'no-cache'
            },
            'body': json.dumps(oauth_response)
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
