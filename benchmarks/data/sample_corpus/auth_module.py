"""
User Authentication Module

This module provides secure user authentication functionality including
password hashing, token generation, and session management.
"""

import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class User:
    """
    Represents a user in the system.
    
    Attributes:
        username: Unique username
        email: User's email address
        created_at: Account creation timestamp
    """
    
    def __init__(self, username: str, email: str, password_hash: str):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = datetime.now()
        self.last_login: Optional[datetime] = None
        self.failed_attempts = 0
        self.is_locked = False
    
    def check_password(self, password: str) -> bool:
        """
        Verify password against stored hash.
        
        Args:
            password: Plain text password to check
            
        Returns:
            True if password matches, False otherwise
        """
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return secrets.compare_digest(password_hash, self.password_hash)
    
    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.now()
        self.failed_attempts = 0
    
    def increment_failed_attempts(self):
        """Track failed login attempts and lock account if necessary."""
        self.failed_attempts += 1
        if self.failed_attempts >= 5:
            self.is_locked = True


class AuthenticationManager:
    """
    Manages user authentication and session tokens.
    
    This class handles:
    - User login/logout
    - Token generation and validation
    - Session management
    - Account lockout policies
    """
    
    def __init__(self, token_expiry_hours: int = 24):
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.token_expiry_hours = token_expiry_hours
    
    def register_user(self, username: str, email: str, password: str) -> User:
        """
        Register a new user.
        
        Args:
            username: Desired username
            email: User's email address
            password: Plain text password (will be hashed)
            
        Returns:
            Newly created User object
            
        Raises:
            ValueError: If username already exists
        """
        if username in self.users:
            raise ValueError(f"Username '{username}' already exists")
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        user = User(username, email, password_hash)
        self.users[username] = user
        return user
    
    def authenticate(self, username: str, password: str) -> str:
        """
        Authenticate user and create session.
        
        Args:
            username: Username to authenticate
            password: Password to verify
            
        Returns:
            Session token string
            
        Raises:
            AuthenticationError: If authentication fails
        """
        user = self.users.get(username)
        
        if user is None:
            raise AuthenticationError("Invalid username or password")
        
        if user.is_locked:
            raise AuthenticationError("Account is locked due to too many failed attempts")
        
        if not user.check_password(password):
            user.increment_failed_attempts()
            raise AuthenticationError("Invalid username or password")
        
        # Generate session token
        token = secrets.token_urlsafe(32)
        expiry = datetime.now() + timedelta(hours=self.token_expiry_hours)
        
        self.sessions[token] = {
            "username": username,
            "expiry": expiry,
            "created_at": datetime.now()
        }
        
        user.update_last_login()
        return token
    
    def validate_token(self, token: str) -> Optional[str]:
        """
        Validate session token.
        
        Args:
            token: Session token to validate
            
        Returns:
            Username if token is valid, None otherwise
        """
        session = self.sessions.get(token)
        
        if session is None:
            return None
        
        if datetime.now() > session["expiry"]:
            # Token expired, remove from sessions
            del self.sessions[token]
            return None
        
        return session["username"]
    
    def logout(self, token: str):
        """
        End user session.
        
        Args:
            token: Session token to invalidate
        """
        if token in self.sessions:
            del self.sessions[token]
    
    def cleanup_expired_sessions(self):
        """Remove all expired session tokens."""
        now = datetime.now()
        expired_tokens = [
            token for token, session in self.sessions.items()
            if now > session["expiry"]
        ]
        for token in expired_tokens:
            del self.sessions[token]


# Example usage
if __name__ == "__main__":
    # Initialize authentication manager
    auth_manager = AuthenticationManager(token_expiry_hours=12)
    
    # Register a new user
    user = auth_manager.register_user(
        username="john_doe",
        email="john@example.com",
        password="SecurePassword123!"
    )
    print(f"Registered user: {user.username}")
    
    # Authenticate user
    try:
        token = auth_manager.authenticate("john_doe", "SecurePassword123!")
        print(f"Login successful! Token: {token[:16]}...")
        
        # Validate token
        username = auth_manager.validate_token(token)
        print(f"Token valid for user: {username}")
        
        # Logout
        auth_manager.logout(token)
        print("User logged out")
    except AuthenticationError as e:
        print(f"Authentication failed: {e}")
