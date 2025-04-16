from app import app, db
from models import User
import os
from migrations.add_balance_column import upgrade as add_balance_column
from migrations.add_is_mining_column import upgrade as add_is_mining_column
from add_new_columns import add_new_columns

def init_db():
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Run migrations
        try:
            add_balance_column()
            print("Balance column migration completed")
        except Exception as e:
            print(f"Error in balance column migration: {e}")
            
        try:
            add_is_mining_column()
            print("Is mining column migration completed")
        except Exception as e:
            print(f"Error in is mining column migration: {e}")
            
        try:
            add_new_columns()
            print("New columns migration completed")
        except Exception as e:
            print(f"Error in new columns migration: {e}")
            
        # Create a default admin user if it doesn't exist
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(email=admin_email, password=admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f"Created default admin user: {admin_email}")
        else:
            print(f"Admin user already exists: {admin_email}")

if __name__ == '__main__':
    init_db() 