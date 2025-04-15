from flask import Flask
from models import db
from sqlalchemy import text

def upgrade():
    # Create a temporary Flask app context
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aveum.db'
    db.init_app(app)
    
    with app.app_context():
        # Add is_mining column to User table
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE user ADD COLUMN is_mining BOOLEAN DEFAULT FALSE"))
            conn.commit()

def downgrade():
    # Create a temporary Flask app context
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aveum.db'
    db.init_app(app)
    
    with app.app_context():
        # Remove is_mining column from User table
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE user DROP COLUMN is_mining"))
            conn.commit()

if __name__ == "__main__":
    upgrade() 