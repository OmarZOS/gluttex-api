
# Authentication Server Documentation

## Overview
This authentication server is implemented using FastAPI and utilizes an SQLite database to enhance security. It supports user registration, login, password changing, and token generation.

## Features
- **User Registration**: Allows new users to register with a username, email, and password.
- **User Login**: Authenticates users and provides access tokens.
- **Password Changing**: Allows users to change their passwords.
- **Token Generation**: Generates and validates access tokens for authenticated users.

## Database
The server uses an SQLite database for storing user information. This enhances security by keeping user data within a contained environment.

## Endpoints

### Registration
**URL**: `/users/`  
**Method**: `POST`  
**Request Body**:
```json
{
    "username": "string",
    "email": "string",
    "phone_number": "string",
    "password": "string",
    "first_name": "string",
    "last_name": "string",
    "date_of_birth": "string",
    "gender": "string",
    "profile_picture": "binary",
    "roles": "string",
    "last_login": "string",
    "login_count": "integer",
    "failed_login_attempts": "integer",
    "account_locked": "boolean",
    "mfa_enabled": "boolean"
}
```
**Response**:
```json
{
    "id_app_user": "integer",
    "username": "string",
    "email": "string",
    "phone_number": "string",
    "first_name": "string",
    "last_name": "string",
    "date_of_birth": "string",
    "gender": "string",
    "profile_picture": "binary",
    "roles": "string",
    "last_login": "string",
    "login_count": "integer",
    "failed_login_attempts": "integer",
    "account_locked": "boolean",
    "mfa_enabled": "boolean",
    "created_at": "datetime",
    "updated_at": "datetime",
    "deleted_at": "datetime"
}
```

### Login
**URL**: `/token`  
**Method**: `POST`  
**Request Body**:
```json
{
    "username": "string",
    "password": "string"
}
```
**Response**:
```json
{
    "access_token": "string",
    "token_type": "string"
}
```

### Change Password
**URL**: `/change-password/`  
**Method**: `POST`  
**Request Body**:
```json
{
    "username": "string",
    "current_password": "string",
    "new_password": "string"
}
```
**Response**:
```json
{
    "message": "Password updated successfully"
}
```

## Token Authentication
The server uses OAuth2 with password (and hashing) bearer tokens. This ensures that each request to the protected endpoints is authenticated.

## Certification

    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout certificates/key.pem -out certficates/cert.pem -config cert.cnf


## Setup
To set up the authentication server, follow these steps:
1. Clone the repository.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Run the server using `uvicorn main:app --reload`.
4. The server will be available at `http://localhost:8000`.

## Usage
You can interact with the authentication server using any HTTP client like `curl`, Postman, or by integrating it with your frontend application.

## Security
- Passwords are hashed using a secure hashing algorithm before being stored in the database.
- The server uses token-based authentication to protect endpoints.

## Conclusion
This authentication server provides a secure and efficient way to manage user authentication and authorization. It can be easily integrated into any web application to enhance security and user management.
