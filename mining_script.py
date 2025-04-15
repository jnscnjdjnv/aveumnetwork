import time
import requests
from datetime import datetime
from app import app, db
from models import User

def update_mining_status(user_id, is_mining):
    with app.app_context():
        user = User.query.get(user_id)
        if user:
            user.is_mining = is_mining
            db.session.commit()

def mine_rewards(user_id):
    with app.app_context():
        user = User.query.get(user_id)
        if not user or not user.is_mining:
            return

        # Simulate mining process
        while user.is_mining:
            try:
                # Add mining reward (example: 0.001 per cycle)
                reward = 0.001
                user.balance = float(user.balance or 0) + reward
                user.total_rewards = float(user.total_rewards or 0) + reward
                db.session.commit()

                # Log the mining activity
                print(f"[{datetime.now()}] User {user.email} mined {reward} coins")

                # Wait for 1 minute before next mining cycle
                time.sleep(60)

            except Exception as e:
                print(f"Error during mining: {str(e)}")
                time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    # This script can be run as a separate process for each user
    import sys
    if len(sys.argv) > 1:
        user_id = int(sys.argv[1])
        mine_rewards(user_id) 