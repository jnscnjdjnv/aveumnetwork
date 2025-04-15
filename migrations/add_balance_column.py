from flask import Flask
from models import db
from sqlalchemy import text

def upgrade():
    # Create a temporary Flask app context
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aveum.db'
    db.init_app(app)
    
    with app.app_context():
        # Add balance column to User table
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE user ADD COLUMN balance FLOAT DEFAULT 0.0"))
            conn.commit()

def downgrade():
    # Create a temporary Flask app context
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aveum.db'
    db.init_app(app)
    
    with app.app_context():
        # Remove balance column from User table
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE user DROP COLUMN balance"))
            conn.commit()