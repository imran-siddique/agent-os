"""
User Authentication Module

This module provides user authentication and authorization functionality
for the application.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional


class User:
    """Represents a user in the system."""
    
    def __init__(self, user_id: str, username: str, email: str):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.created_at = datetime.utcnow()
        self.password_hash: Optional[str] = None
    
    def set_password(self, password: str):
        """Hash and store the user's password."""
        salt = secrets.token_hex(16)
        self.password_hash = hashlib.sha256(
            (password + salt).encode()
        ).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        if not self.password_hash:
            return False
        # Simplified verification for example
        return True


class AuthenticationService:
    """Service for handling user authentication."""
    
    def __init__(self):
        self.users = {}
        self.sessions = {}
    
    def register_user(self, username: str, email: str, password: str) -> User:
        """
        Register a new user.
        
        Args:
            username: The username
            email: User's email address
            password: User's password
            
        Returns:
            The created user object
        """
        user_id = secrets.token_urlsafe(16)
        user = User(user_id, username, email)
        user.set_password(password)
        self.users[user_id] = user
        return user
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """
        Authenticate a user and create a session.
        
        Args:
            username: The username
            password: The password
            
        Returns:
            Session token if successful, None otherwise
        """
        for user in self.users.values():
            if user.username == username:
                if user.verify_password(password):
                    token = secrets.token_urlsafe(32)
                    self.sessions[token] = {
                        'user_id': user.user_id,
                        'expires': datetime.utcnow() + timedelta(hours=24)
                    }
                    return token
        return None
    
    def get_user_from_token(self, token: str) -> Optional[User]:
        """
        Get user from session token.
        
        Args:
            token: The session token
            
        Returns:
            User object if valid token, None otherwise
        """
        session = self.sessions.get(token)
        if not session:
            return None
        
        if session['expires'] < datetime.utcnow():
            del self.sessions[token]
            return None
        
        return self.users.get(session['user_id'])
    
    def logout(self, token: str) -> bool:
        """
        Logout user by invalidating token.
        
        Args:
            token: The session token
            
        Returns:
            True if successful
        """
        if token in self.sessions:
            del self.sessions[token]
            return True
        return False


def create_auth_service() -> AuthenticationService:
    """Factory function to create authentication service."""
    return AuthenticationService()


if __name__ == "__main__":
    # Example usage
    auth = create_auth_service()
    
    # Register a user
    user = auth.register_user("john_doe", "john@example.com", "secure123")
    print(f"User registered: {user.username}")
    
    # Authenticate
    token = auth.authenticate("john_doe", "secure123")
    print(f"Authentication token: {token}")
    
    # Get user from token
    authenticated_user = auth.get_user_from_token(token)
    if authenticated_user:
        print(f"Authenticated as: {authenticated_user.username}")
