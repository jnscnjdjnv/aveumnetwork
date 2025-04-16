from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime
import os
import json
import asyncio
import aiohttp
from dotenv import load_dotenv
import aveum_api
import threading
from models import db, User

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aveum.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Suppress the deprecation warning
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Load environment variables
load_dotenv()

# Initialize database
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            
            if not email or not password:
                flash('Please provide both email and password')
                return render_template('login.html')
                
            user = User.query.filter_by(email=email).first()
            
            if user and user.password == password:  # In production, use proper password hashing
                login_user(user)
                user.last_login_time = datetime.now()
                db.session.commit()
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password')
        except Exception as e:
            app.logger.error(f"Login error: {str(e)}")
            flash('An error occurred during login. Please try again.')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            
            if not email or not password:
                flash('Please provide both email and password')
                return render_template('register.html')
            
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email already registered')
                return render_template('register.html')
            
            # Create new user
            new_user = User(email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            
            # Log in the new user
            login_user(new_user)
            return redirect(url_for('dashboard'))
        except Exception as e:
            app.logger.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.')
            
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

def load_env_credentials(for_display=False):
    """Load Aveum credentials from .env file or return default placeholders"""
    load_dotenv()
    
    if for_display:
        # Return default placeholder values for display
        return {
            'email': 'your-email@gmail.com',
            'password': 'your-password'
        }
    else:
        # Return actual credentials for API calls
        return {
            'email': os.getenv('AVEUM_EMAIL'),
            'password': os.getenv('AVEUM_PASSWORD')
        }

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

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        try:
            email = request.form.get('aveum_email')
            password = request.form.get('aveum_password')
            
            if not email or not password:
                flash('Please provide both email and password')
                return render_template('settings.html')
            
            # Update user's Aveum credentials
            current_user.aveum_email = email
            current_user.aveum_password = password
            
            # Try to login with new credentials
            login_result = asyncio.run(aveum_api.login(email, password))
            
            if login_result['success']:
                current_user.aveum_token = login_result['token']
                current_user.device_id = login_result['device_id']
                current_user.device_model = login_result['device_model']
                current_user.platform_version = login_result['platform_version']
                db.session.commit()
                flash('Aveum credentials updated successfully!')
            else:
                flash(f'Failed to verify credentials: {login_result.get("error", "Unknown error")}')
        except Exception as e:
            app.logger.error(f"Settings update error: {str(e)}")
            flash('An error occurred while updating settings. Please try again.')
            
    # Pass placeholder credentials for display
    env_credentials = load_env_credentials(for_display=True)
    return render_template('settings.html', env_credentials=env_credentials)

@app.route('/api/test_credentials', methods=['POST'])
@login_required
def test_credentials():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required'})
    
    try:
        result = aveum_api.login(email, password)
        if result.get('success'):
            return jsonify({'success': True, 'message': 'Credentials are valid'})
        else:
            return jsonify({'success': False, 'message': result.get('message', 'Invalid credentials')})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error testing credentials: {str(e)}'})

@app.route('/api/start-mining', methods=['POST'])
@login_required
def start_mining():
    if current_user.is_mining:
        return jsonify({'error': 'Mining is already in progress'}), 400
    
    current_user.is_mining = True
    db.session.commit()
    
    # Start mining process in a separate thread
    from threading import Thread
    from mining_script import mine_rewards
    thread = Thread(target=mine_rewards, args=(current_user.id,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Mining started successfully'})

@app.route('/api/stop-mining', methods=['POST'])
@login_required
def stop_mining():
    if not current_user.is_mining:
        return jsonify({'error': 'Mining is not in progress'}), 400
    
    current_user.is_mining = False
    db.session.commit()
    
    return jsonify({'message': 'Mining stopped successfully'})

@app.route('/api/toggle_auto_like', methods=['POST'])
@login_required
def toggle_auto_like():
    # Try to use existing token first
    if current_user.aveum_token:
        current_user.auto_like_active = not current_user.auto_like_active
        action = "started" if current_user.auto_like_active else "stopped"
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Auto-like {action}."
        current_user.last_activity_log = log_entry + "\n" + (current_user.last_activity_log or "")
        db.session.commit()
        
        if current_user.auto_like_active:
            # Store user ID before creating thread
            user_id = current_user.id
            threading.Thread(
                target=lambda: asyncio.run(run_auto_like(user_id)),
                daemon=True
            ).start()
        
        return jsonify({
            'success': True,
            'auto_like_active': current_user.auto_like_active,
            'message': f"Auto-like {action} successfully"
        })
    
    # If no token, try to login with .env credentials
    env_credentials = load_env_credentials()
    if not env_credentials['email'] or not env_credentials['password']:
        return jsonify({'success': False, 'error': 'Please set your Aveum credentials in Settings'}), 400
    
    # Try to login
    login_result = asyncio.run(aveum_api.login(env_credentials['email'], env_credentials['password']))
    if not login_result['success']:
        return jsonify({'success': False, 'error': f"Login failed: {login_result.get('error', 'Unknown error')}"}), 500
    
    # Update user token and device info
    current_user.aveum_token = login_result['token']
    current_user.device_id = login_result['device_id']
    current_user.device_model = login_result['device_model']
    current_user.platform_version = login_result['platform_version']
    
    # Toggle auto-like
    current_user.auto_like_active = not current_user.auto_like_active
    action = "started" if current_user.auto_like_active else "stopped"
    log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Auto-like {action} after login."
    current_user.last_activity_log = log_entry + "\n" + (current_user.last_activity_log or "")
    db.session.commit()
    
    if current_user.auto_like_active:
        # Store user ID before creating thread
        user_id = current_user.id
        threading.Thread(
            target=lambda: asyncio.run(run_auto_like(user_id)),
            daemon=True
        ).start()
    
    return jsonify({
        'success': True,
        'auto_like_active': current_user.auto_like_active,
        'message': f"Auto-like {action} successfully after login"
    })

@app.route('/api/refresh_token', methods=['POST'])
@login_required
def refresh_token():
    if not current_user.aveum_email or not current_user.aveum_password:
        return jsonify({'error': 'Please set your Aveum credentials first'}), 400
    
    # Login to Aveum to get a new token
    login_result = asyncio.run(aveum_api.login(current_user.aveum_email, current_user.aveum_password))
    
    if login_result['success']:
        current_user.aveum_token = login_result['token']
        current_user.device_id = login_result['device_id']
        current_user.device_model = login_result['device_model']
        current_user.platform_version = login_result['platform_version']
        
        # Update activity log
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Token refreshed. New device: {current_user.device_model} (ID: {current_user.device_id})"
        current_user.last_activity_log = log_entry + "\n" + (current_user.last_activity_log or "")
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Token refreshed successfully'})
    else:
        return jsonify({'success': False, 'error': f"Token refresh failed: {login_result.get('error', 'Unknown error')}"}), 500

@app.route('/api/status', methods=['GET'])
@login_required
def get_status():
    if not current_user.aveum_token:
        return jsonify({'error': 'Not logged in to Aveum'}), 400
    
    # Get hub status from Aveum
    hub_status = asyncio.run(aveum_api.get_hub_status(current_user.aveum_token))
    
    if hub_status['success']:
        data = hub_status['data']
        
        # Update user stats if mining is active
        if data.get('isHub') and current_user.mining_active:
            if 'currentEarning' in data:
                current_user.total_rewards = float(data['currentEarning'])
                current_user.balance = float(data['currentEarning'])  # Update current balance
                db.session.commit()
        
        return jsonify({
            'success': True,
            'aveum_email': current_user.aveum_email or "Not set",
            'login_status': bool(current_user.aveum_token),
            'device_id': current_user.device_id or "Not set",
            'device_model': current_user.device_model or "Not set",
            'platform_version': current_user.platform_version or "Not set",
            'is_mining': current_user.is_mining,
            'current_balance': float(current_user.balance or 0),
            'total_rewards': float(current_user.total_rewards or 0),
            'mining_sessions_completed': current_user.mining_sessions_completed or 0,
            'mining_errors': current_user.mining_errors or 0,
            'auto_like_active': current_user.auto_like_active,
            'total_likes': current_user.total_likes or 0,
            'daily_likes': current_user.daily_likes or 0,
            'like_errors': current_user.like_errors or 0,
            'is_banned': current_user.is_banned,
            'last_ban_check_time': current_user.last_ban_check_time.strftime('%Y-%m-%d %H:%M:%S') if current_user.last_ban_check_time else 'Never',
            'last_activity': current_user.last_activity_log or "No activity recorded"
        })
    else:
        return jsonify({'success': False, 'error': f"Failed to get status: {hub_status.get('error', 'Unknown error')}"}), 500

@app.route('/api/get_activity_log', methods=['GET'])
@login_required
def get_activity_log():
    return jsonify({
        'status': 'success',
        'activity_log': current_user.last_activity_log or "No activity recorded yet."
    })

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/aveum_credentials', methods=['GET', 'POST'])
@login_required
def aveum_credentials():
    if request.method == 'POST':
        try:
            email = request.form.get('aveum_email')
            password = request.form.get('aveum_password')
            
            if not email or not password:
                flash('Please provide both email and password', 'warning')
                return render_template('aveum_credentials.html')
            
            # Try to login with new credentials first
            app.logger.info(f"Testing Aveum login for user {current_user.id} with email {email}")
            login_result = asyncio.run(aveum_api.login(email, password))
            
            if login_result['success']:
                # Only save credentials if login was successful
                try:
                    # Save to .env file first
                    save_env_credentials(email, password)
                    app.logger.info(f"Saved Aveum credentials to .env for user {current_user.id}")
                    
                    # Then update user record
                    current_user.aveum_email = email
                    current_user.aveum_password = password
                    current_user.aveum_token = login_result['token']
                    current_user.device_id = login_result['device_id']
                    current_user.device_model = login_result['device_model']
                    current_user.platform_version = login_result['platform_version']
                    db.session.commit()
                    app.logger.info(f"Updated Aveum credentials in database for user {current_user.id}")
                    
                    flash('Aveum credentials saved and verified successfully!', 'success')
                except Exception as save_error:
                    app.logger.error(f"Failed to save credentials: {str(save_error)}")
                    db.session.rollback()
                    flash('Login successful but failed to save credentials. Please try again.', 'danger')
            else:
                error_msg = login_result.get('error', 'Unknown error')
                app.logger.error(f"Aveum login failed for user {current_user.id}: {error_msg}")
                flash(f'Login failed: {error_msg}', 'danger')
        except Exception as e:
            app.logger.error(f"Aveum credentials update error for user {current_user.id}: {str(e)}")
            flash('An error occurred while updating credentials. Please try again.', 'danger')
            db.session.rollback()
    
    return render_template('aveum_credentials.html')

@app.route('/api/mining-status')
@login_required
def get_mining_status():
    try:
        return jsonify({
            'is_mining': current_user.is_mining,
            'current_balance': float(current_user.balance or 0),
            'total_rewards': float(current_user.total_rewards or 0)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-ban', methods=['POST'])
@login_required
def check_ban():
    if not current_user.aveum_token:
        return jsonify({'success': False, 'error': 'Not logged in to Aveum'}), 400
    
    try:
        # Check ban status
        ban_result = asyncio.run(aveum_api.check_user_ban(current_user.aveum_token))
        
        if ban_result['success']:
            data = ban_result['data']
            is_banned = data.get('banned', False)
            
            # Update user ban status
            current_user.is_banned = is_banned
            current_user.last_ban_check_time = datetime.now()
            
            # Add to activity log
            ban_status = "Banned" if is_banned else "Not banned"
            log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ban check: {ban_status}"
            current_user.last_activity_log = log_entry + "\n" + (current_user.last_activity_log or "")
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'is_banned': is_banned,
                'message': f"Account is {ban_status}"
            })
        else:
            return jsonify({
                'success': False,
                'error': f"Failed to check ban status: {ban_result.get('error', 'Unknown error')}"
            }), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/switch-mode', methods=['POST'])
@login_required
def switch_mode():
    if not current_user.aveum_token:
        return jsonify({'success': False, 'error': 'Not logged in to Aveum'}), 400
    
    try:
        # Toggle between mining and auto-like modes
        if current_user.mining_active:
            # Switch from mining to auto-like
            current_user.mining_active = False
            current_user.auto_like_active = True
            mode = "Auto-like"
        else:
            # Switch from auto-like to mining
            current_user.mining_active = True
            current_user.auto_like_active = False
            mode = "Mining"
        
        # Add to activity log
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Switched to {mode} mode"
        current_user.last_activity_log = log_entry + "\n" + (current_user.last_activity_log or "")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f"Switched to {mode} mode successfully"
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Background tasks
async def run_auto_like(user_id):
    """Background task to run auto-like process"""
    from flask import current_app
    
    with current_app.app_context():
        user = User.query.get(user_id)
        if not user or not user.auto_like_active:
            return
        
        while user.auto_like_active:
            try:
                if not user.aveum_token:
                    user.auto_like_active = False
                    db.session.commit()
                    break
                    
                # Check if token is valid
                profile_check = await aveum_api.get_user_profile(user.aveum_token)
                if not profile_check['success']:
                    # Try to refresh token using .env credentials
                    env_credentials = load_env_credentials()
                    if env_credentials['email'] and env_credentials['password']:
                        login_result = await aveum_api.login(env_credentials['email'], env_credentials['password'])
                        if login_result['success']:
                            user.aveum_token = login_result['token']
                            user.device_id = login_result['device_id']
                            user.device_model = login_result['device_model']
                            user.platform_version = login_result['platform_version']
                            db.session.commit()
                        else:
                            log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Auto-like stopped: Failed to refresh token"
                            user.last_activity_log = log_entry + "\n" + (user.last_activity_log or "")
                            user.auto_like_active = False
                            db.session.commit()
                            return
                
                # Continue with auto-like process
                processed_user_ids = set()
                page = 1
                max_pages = 5
                
                while page <= max_pages and user.auto_like_active:
                    # Get users from discover feed
                    feed_result = await aveum_api.get_discover_feed(user.aveum_token, page, 20)
                    
                    if not feed_result['success']:
                        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetching discover feed: {feed_result.get('error', 'Unknown error')}"
                        user.last_activity_log = log_entry + "\n" + (user.last_activity_log or "")
                        db.session.commit()
                        break
                    
                    data = feed_result['data']
                    users = []
                    
                    if 'users' in data and isinstance(data['users'], list):
                        users = data['users']
                    elif 'posts' in data and isinstance(data['posts'], list):
                        users = [{'id': post.get('user_id') or post.get('id'), 
                                'username': post.get('username'), 
                                'is_liked': post.get('liked')} for post in data['posts']]
                    
                    liked_count = 0
                    
                    for user_data in users:
                        if not user.auto_like_active:
                            break
                        
                        user_id = user_data.get('id')
                        if not user_id or user_id in processed_user_ids:
                            continue
                        
                        if user_data.get('is_liked'):
                            processed_user_ids.add(user_id)
                            continue
                        
                        # Like the user
                        like_result = await aveum_api.toggle_like(user.aveum_token, user_id)
                        
                        if like_result['success']:
                            processed_user_ids.add(user_id)
                            user.total_likes += 1
                            liked_count += 1
                            
                            username = user_data.get('username', 'Unknown')
                            log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Liked user: {username} (ID: {user_id})"
                            user.last_activity_log = log_entry + "\n" + (user.last_activity_log or "")
                            db.session.commit()
                        
                        # Random delay between likes
                        await asyncio.sleep(aveum_api.get_random_delay(2, 5))
                    
                    if liked_count == 0 and page > 1:
                        break
                    
                    page += 1
                    
                    if page <= max_pages and user.auto_like_active:
                        await asyncio.sleep(aveum_api.get_random_delay(5, 10))
                
                # Take a break before next cycle
                if user.auto_like_active:
                    delay = aveum_api.get_random_delay(60, 120)
                    log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Auto-like cycle completed. Next run in {delay} seconds."
                    user.last_activity_log = log_entry + "\n" + (user.last_activity_log or "")
                    db.session.commit()
                    await asyncio.sleep(delay)
            
            except Exception as error:
                print(f"Error in auto-like process: {str(error)}")
                await asyncio.sleep(30)  # Wait before retrying

# Mining check task
async def check_mining_status():
    """Background task to check mining status and refresh token if needed"""
    with app.app_context():
        while True:
            users = User.query.filter_by(mining_active=True).all()
            
            for user in users:
                try:
                    # Check hub status
                    hub_status = await aveum_api.get_hub_status(user.aveum_token)
                    
                    if not hub_status['success']:
                        # Try to refresh token using .env credentials
                        env_credentials = load_env_credentials()
                        if env_credentials['email'] and env_credentials['password']:
                            login_result = await aveum_api.login(env_credentials['email'], env_credentials['password'])
                            if login_result['success']:
                                user.aveum_token = login_result['token']
                                user.device_id = login_result['device_id']
                                user.device_model = login_result['device_model']
                                user.platform_version = login_result['platform_version']
                                db.session.commit()
                                
                                # Try hub status again with new token
                                hub_status = await aveum_api.get_hub_status(user.aveum_token)
                    
                    if hub_status['success']:
                        data = hub_status['data']
                        
                        if data.get('isHub'):
                            if 'currentEarning' in data:
                                user.total_rewards = float(data['currentEarning'])
                            
                            if data.get('remainingTime', 0) <= 0.001:
                                # Mining complete, claim reward and start new session
                                claim_result = await aveum_api.claim_reward(user.aveum_token)
                                
                                if claim_result['success']:
                                    log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Mining complete. Reward claimed."
                                    user.last_activity_log = log_entry + "\n" + (user.last_activity_log or "")
                                    
                                    # Start new mining session
                                    mining_result = await aveum_api.start_hub_mining(user.aveum_token)
                                    
                                    if mining_result['success']:
                                        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] New mining session started."
                                        user.last_activity_log = log_entry + "\n" + (user.last_activity_log or "")
                                    else:
                                        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Failed to start new mining session: {mining_result.get('error', 'Unknown error')}"
                                        user.last_activity_log = log_entry + "\n" + (user.last_activity_log or "")
                                else:
                                    log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Failed to claim reward: {claim_result.get('error', 'Unknown error')}"
                                    user.last_activity_log = log_entry + "\n" + (user.last_activity_log or "")
                        else:
                            # Mining not active, start it
                            mining_result = await aveum_api.start_hub_mining(user.aveum_token)
                            
                            if mining_result['success']:
                                log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Mining was inactive. Started automatically."
                                user.last_activity_log = log_entry + "\n" + (user.last_activity_log or "")
                            else:
                                log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Failed to start mining: {mining_result.get('error', 'Unknown error')}"
                                user.last_activity_log = log_entry + "\n" + (user.last_activity_log or "")
                    
                    db.session.commit()
                except Exception as error:
                    print(f"Error in mining status check: {str(error)}")
            
            await asyncio.sleep(30)  # Check every 30 seconds

def run_async_loop():
    """Run the asyncio event loop in a separate thread"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(check_mining_status())
    loop.run_forever()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Start background tasks in a separate thread
        background_thread = threading.Thread(target=run_async_loop, daemon=True)
        background_thread.start()
        
        # Run the Flask app
        app.run(debug=True) 