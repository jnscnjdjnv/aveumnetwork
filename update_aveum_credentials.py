#!/usr/bin/env python
"""
Aveum Credentials Update Tool

This script helps users update their Aveum credentials after registration.
It will:
1. Connect to the database
2. Find the user by email
3. Update their Aveum credentials
4. Test the credentials with the Aveum API
5. Save the credentials to the database and .env file
"""

import os
import sys
import asyncio
import getpass
from flask import Flask
from models import db, User
import aveum_api
from dotenv import load_dotenv

# Create a temporary Flask app context
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aveum.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def save_env_credentials(email, password):
    """Save Aveum credentials to .env file"""
    env_path = os.path.join(os.getcwd(), '.env')
    
    # Read existing .env content
    env_content = {}
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    # Remove any existing quotes
                    value = value.strip('"\'')
                    env_content[key] = value
    
    # Update credentials
    env_content['AVEUM_EMAIL'] = email
    env_content['AVEUM_PASSWORD'] = password
    
    # Write back to .env file with proper quoting
    with open(env_path, 'w') as f:
        for key, value in env_content.items():
            # Quote the value if it contains spaces or special characters
            if any(c in value for c in ' \t\n\r\'"'):
                value = f'"{value}"'
            f.write(f"{key}={value}\n")
    
    print(f"Credentials saved to {env_path}")

async def update_credentials(user_email, aveum_email, aveum_password):
    """Update Aveum credentials for a user"""
    with app.app_context():
        # Find the user
        user = User.query.filter_by(email=user_email).first()
        if not user:
            print(f"Error: User with email {user_email} not found")
            return False
        
        # Try to login with new credentials
        print(f"Testing Aveum login with email {aveum_email}...")
        login_result = await aveum_api.login(aveum_email, aveum_password)
        
        if login_result['success']:
            # Save to .env file
            save_env_credentials(aveum_email, aveum_password)
            
            # Update user record
            user.aveum_email = aveum_email
            user.aveum_password = aveum_password
            user.aveum_token = login_result['token']
            user.device_id = login_result['device_id']
            user.device_model = login_result['device_model']
            user.platform_version = login_result['platform_version']
            db.session.commit()
            
            print("Aveum credentials updated successfully!")
            print(f"Device ID: {user.device_id}")
            print(f"Device Model: {user.device_model}")
            print(f"Platform Version: {user.platform_version}")
            return True
        else:
            error_msg = login_result.get('error', 'Unknown error')
            print(f"Login failed: {error_msg}")
            return False

def main():
    print("=" * 50)
    print("Aveum Credentials Update Tool")
    print("=" * 50)
    
    # Get user email
    user_email = input("Enter your registered email: ")
    
    # Get Aveum credentials
    aveum_email = input("Enter your Aveum email: ")
    aveum_password = getpass.getpass("Enter your Aveum password: ")
    
    # Confirm
    print("\nPlease confirm your credentials:")
    print(f"User Email: {user_email}")
    print(f"Aveum Email: {aveum_email}")
    confirm = input("Is this correct? (y/n): ")
    
    if confirm.lower() != 'y':
        print("Operation cancelled")
        return
    
    # Update credentials
    print("\nUpdating credentials...")
    success = asyncio.run(update_credentials(user_email, aveum_email, aveum_password))
    
    if success:
        print("\nYour Aveum credentials have been updated successfully!")
        print("You can now use the dashboard to manage your Aveum account.")
    else:
        print("\nFailed to update Aveum credentials. Please check your credentials and try again.")

if __name__ == "__main__":
    main() 