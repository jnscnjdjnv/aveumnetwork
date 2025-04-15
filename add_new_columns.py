from app import app, db
from models import User
from sqlalchemy import text, inspect

def add_new_columns():
    with app.app_context():
        inspector = inspect(db.engine)
        existing_columns = [col['name'] for col in inspector.get_columns('user')]
        
        # Define columns to add with their SQL definitions
        columns_to_add = {
            'mining_start_time': 'DATETIME',
            'mining_end_time': 'DATETIME',
            'mining_sessions_completed': 'INTEGER DEFAULT 0',
            'last_like_time': 'DATETIME',
            'daily_likes': 'INTEGER DEFAULT 0',
            'daily_rewards': 'FLOAT DEFAULT 0.0',
            'last_reward_claim_time': 'DATETIME',
            'mining_errors': 'INTEGER DEFAULT 0',
            'like_errors': 'INTEGER DEFAULT 0',
            'is_banned': 'BOOLEAN DEFAULT FALSE',
            'last_ban_check_time': 'DATETIME'
        }
        
        # Add columns that don't exist yet
        for column_name, column_type in columns_to_add.items():
            if column_name not in existing_columns:
                sql = f'ALTER TABLE user ADD COLUMN {column_name} {column_type}'
                db.session.execute(text(sql))
        
        db.session.commit()
        print("Successfully added new columns to User table")

if __name__ == '__main__':
    add_new_columns() 