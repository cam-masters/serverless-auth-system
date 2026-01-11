"""
Shared utilities for DynamoDB operations and KMS encryption
"""
import os
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')

# Environment variables
TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'users')

table = dynamodb.Table(TABLE_NAME)


def create_user(
        user_id: str,
        email: str,
        first_name: str,
        last_name: str,
        password_hash: str) -> bool:
    """
    Create a new user in DynamoDB
    
    Args:
        user_id: Unique user identifier
        email: User's email address
        password_hash: Hashed password
        encrypted_data: Optional dictionary of encrypted user data
        
    Returns:
        True if successful, False otherwise
    """
    try:
        item = {
            'userId': user_id,
            'email': email,
            'firstName': first_name,
            'lastName': last_name,
            'passwordHash': password_hash,
            'createdAt': datetime.now(datetime.timezone.utc).isoformat(),
            'updatedAt': datetime.now(datetime.timezone.utc).isoformat()
        }
        
        table.put_item(
            Item=item,
            ConditionExpression='attribute_not_exists(userId)'
        )
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            print(f"User {user_id} already exists")
        else:
            print(f"Error creating user: {e}")
        return False


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a user by email address
    
    Args:
        email: User's email address
        
    Returns:
        User data if found, None otherwise
    """
    try:
        response = table.query(
            IndexName='Email_Index',
            KeyConditionExpression=Key('email').eq(email)
        )
        
        items = response.get('Items', [])
        return items[0] if items else None
    except ClientError as e:
        print(f"Error getting user: {e}")
        return None
