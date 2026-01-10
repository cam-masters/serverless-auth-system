"""
Shared utilities for DynamoDB operations and KMS encryption
"""
import os
import boto3
import json
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
kms_client = boto3.client('kms')

# Environment variables
TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'users')
KMS_KEY_ID = os.environ.get('KMS_KEY_ID', 'alias/auth-system-key')

table = dynamodb.Table(TABLE_NAME)


def encrypt_data(plaintext: str) -> str:
    """
    Encrypt data using KMS
    
    Args:
        plaintext: The string to encrypt
        
    Returns:
        Base64 encoded encrypted data
    """
    try:
        response = kms_client.encrypt(
            KeyId=KMS_KEY_ID,
            Plaintext=plaintext.encode('utf-8')
        )
        # Return base64 encoded ciphertext
        import base64
        return base64.b64encode(response['CiphertextBlob']).decode('utf-8')
    except ClientError as e:
        print(f"Error encrypting data: {e}")
        raise


def decrypt_data(ciphertext: str) -> str:
    """
    Decrypt data using KMS
    
    Args:
        ciphertext: Base64 encoded encrypted data
        
    Returns:
        Decrypted plaintext string
    """
    try:
        import base64
        ciphertext_blob = base64.b64decode(ciphertext.encode('utf-8'))
        
        response = kms_client.decrypt(
            CiphertextBlob=ciphertext_blob
        )
        return response['Plaintext'].decode('utf-8')
    except ClientError as e:
        print(f"Error decrypting data: {e}")
        raise


def create_user(user_id: str, email: str, password_hash: str, 
                encrypted_data: Optional[Dict[str, str]] = None) -> bool:
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
        from datetime import datetime
        
        item = {
            'userId': user_id,
            'email': email,
            'passwordHash': password_hash,
            'createdAt': datetime.utcnow().isoformat(),
            'updatedAt': datetime.utcnow().isoformat()
        }
        
        # Add encrypted data if provided
        if encrypted_data:
            item['encryptedData'] = encrypted_data
        
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
        response = table.scan(
            FilterExpression='email = :email',
            ExpressionAttributeValues={':email': email}
        )
        
        items = response.get('Items', [])
        return items[0] if items else None
    except ClientError as e:
        print(f"Error getting user: {e}")
        return None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a user by user ID
    
    Args:
        user_id: Unique user identifier
        
    Returns:
        User data if found, None otherwise
    """
    try:
        response = table.get_item(Key={'userId': user_id})
        return response.get('Item')
    except ClientError as e:
        print(f"Error getting user: {e}")
        return None


def update_user(user_id: str, updates: Dict[str, Any]) -> bool:
    """
    Update user data
    
    Args:
        user_id: Unique user identifier
        updates: Dictionary of fields to update
        
    Returns:
        True if successful, False otherwise
    """
    try:
        from datetime import datetime
        
        # Build update expression
        update_expr = "SET updatedAt = :updated"
        expr_values = {':updated': datetime.utcnow().isoformat()}
        
        for key, value in updates.items():
            update_expr += f", {key} = :{key}"
            expr_values[f":{key}"] = value
        
        table.update_item(
            Key={'userId': user_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_values
        )
        return True
    except ClientError as e:
        print(f"Error updating user: {e}")
        return False
