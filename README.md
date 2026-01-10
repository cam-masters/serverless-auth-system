# Serverless Authentication System

A robust serverless authentication system built with AWS Lambda, DynamoDB, and KMS. This system provides secure user registration and authentication with OAuth 2.0 JWT tokens.

## Features

- **User Registration**: Create new users with email and password
- **User Authentication**: Login with credentials and receive OAuth 2.0 access tokens
- **Password Security**: Passwords are hashed using bcrypt
- **Data Encryption**: Sensitive user data encrypted with AWS KMS
- **JWT Tokens**: OAuth 2.0 compliant bearer tokens for authentication
- **Serverless Architecture**: Built on AWS Lambda for scalability and cost-efficiency
- **Infrastructure as Code**: Fully defined using AWS SAM

## Architecture

```
┌─────────────┐
│ API Gateway │ (To be added)
└──────┬──────┘
       │
       ├───────────────────────────────────┐
       │                                   │
┌──────▼──────────┐              ┌────────▼──────────┐
│ Register Lambda │              │  Login Lambda     │
│  (register_user)│              │  (login_user)     │
└──────┬──────────┘              └────────┬──────────┘
       │                                   │
       ├───────────────────────────────────┤
       │                                   │
   ┌───▼────────┐                  ┌──────▼────┐
   │  DynamoDB  │                  │    KMS    │
   │   Users    │                  │  Encrypt  │
   │   Table    │                  │  Decrypt  │
   └────────────┘                  └───────────┘
```

## Prerequisites

- AWS Account
- AWS CLI configured with appropriate credentials
- AWS SAM CLI installed
- Python 3.11 or higher
- Git

## Project Structure

```
serverless-auth-system/
├── lambda-functions/
│   ├── register_user.py      # User registration handler
│   ├── login_user.py          # User authentication handler
│   ├── db_utils.py            # DynamoDB operations
│   └── auth_utils.py          # Authentication utilities
├── template.yaml              # AWS SAM template
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/cam-masters/serverless-auth-system.git
cd serverless-auth-system
```

### 2. Configure Environment Variables

Copy the example environment file and update with your values:

```bash
cp .env.example .env
```

Edit `.env` and set your JWT secret:

```env
JWT_SECRET=your-secure-random-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### 3. Build the Application

```bash
sam build
```

### 4. Deploy to AWS

For first-time deployment:

```bash
sam deploy --guided
```

Follow the prompts:
- **Stack Name**: `serverless-auth-system`
- **AWS Region**: Your preferred region (e.g., `us-east-1`)
- **Parameter Environment**: `dev`, `staging`, or `prod`
- **Parameter JWTSecret**: Your secure JWT secret key
- **Confirm changes before deploy**: `Y`
- **Allow SAM CLI IAM role creation**: `Y`
- **Save arguments to configuration file**: `Y`

For subsequent deployments:

```bash
sam deploy
```

### 5. Get Stack Outputs

After deployment, retrieve the function names and other outputs:

```bash
aws cloudformation describe-stacks --stack-name serverless-auth-system --query 'Stacks[0].Outputs'
```

## API Usage

### Register a New User

**Endpoint**: `RegisterUserFunction`

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "firstName": "John",
  "lastName": "Doe"
}
```

**Response** (201 Created):
```json
{
  "message": "User created successfully",
  "userId": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Error Responses**:
- `400`: Invalid email format or password too short
- `409`: User already exists
- `500`: Internal server error

### Login / Authenticate

**Endpoint**: `LoginUserFunction`

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 86400,
  "scope": "read write"
}
```

**Error Responses**:
- `400`: Missing email or password
- `401`: Invalid credentials
- `500`: Internal server error

## Testing Locally

### Invoke Lambda Functions Locally

Test the register function:

```bash
sam local invoke RegisterUserFunction -e test-events/register.json
```

Test the login function:

```bash
sam local invoke LoginUserFunction -e test-events/login.json
```

### Create Test Events

Create a `test-events` directory with sample events:

**test-events/register.json**:
```json
{
  "body": "{\"email\":\"test@example.com\",\"password\":\"TestPass123!\",\"firstName\":\"Test\",\"lastName\":\"User\"}"
}
```

**test-events/login.json**:
```json
{
  "body": "{\"email\":\"test@example.com\",\"password\":\"TestPass123!\"}"
}
```

## DynamoDB Schema

### Users Table

| Attribute      | Type   | Description                           |
|----------------|--------|---------------------------------------|
| userId         | String | Primary Key - UUID                    |
| email          | String | User's email (unique)                 |
| passwordHash   | String | Bcrypt hashed password                |
| encryptedData  | Map    | KMS encrypted user information        |
| createdAt      | String | ISO 8601 timestamp                    |
| updatedAt      | String | ISO 8601 timestamp                    |

## Security Considerations

1. **Password Hashing**: Passwords are hashed using bcrypt with automatic salt generation
2. **KMS Encryption**: Personal information (firstName, lastName) is encrypted at rest using AWS KMS
3. **JWT Tokens**: Tokens are signed with HS256 algorithm and include expiration
4. **CORS**: Configured for all origins (`*`) - restrict in production
5. **IAM Roles**: Lambda functions have minimal required permissions
6. **Secrets Management**: JWT secret should be stored in AWS Secrets Manager for production

## Next Steps

### Adding API Gateway

To make the Lambda functions accessible via HTTP, add API Gateway:

1. Update `template.yaml` to include API Gateway resources
2. Add API Gateway events to Lambda functions
3. Configure authorizers for protected endpoints
4. Deploy the updated stack

Example addition to `template.yaml`:

```yaml
RegisterUserFunction:
  Type: AWS::Serverless::Function
  Properties:
    # ... existing properties ...
    Events:
      RegisterApi:
        Type: Api
        Properties:
          Path: /register
          Method: POST
```

### Additional Features to Implement

- [ ] Email verification
- [ ] Password reset flow
- [ ] Refresh token mechanism
- [ ] User profile management
- [ ] Multi-factor authentication (MFA)
- [ ] Rate limiting
- [ ] Session management
- [ ] OAuth social login integration

## Development

### Install Dependencies Locally

```bash
pip install -r requirements.txt
```

### Run Tests

```bash
python -m pytest tests/
```

## Troubleshooting

### Lambda Timeout Issues

Increase the timeout in `template.yaml`:

```yaml
Globals:
  Function:
    Timeout: 60
```

### KMS Permission Errors

Ensure the Lambda execution role has KMS permissions:

```yaml
- Effect: Allow
  Action:
    - 'kms:Decrypt'
    - 'kms:Encrypt'
  Resource: !GetAtt KMSKey.Arn
```

### DynamoDB Access Issues

Verify the Lambda role has DynamoDB permissions for the Users table.

## Cost Estimate

For a low-traffic application (1000 requests/month):
- Lambda: ~$0.20
- DynamoDB: ~$0.25 (Pay-per-request)
- KMS: $1.00 (key storage)
- **Total**: ~$1.45/month

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Author

Cameron Masters

## Support

For issues and questions, please open a GitHub issue in the repository.
