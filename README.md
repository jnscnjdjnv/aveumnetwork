# Aveum Dashboard

A web application for managing Aveum mining and auto-like operations.

## Features

- User authentication (login/register)
- Dashboard with real-time status updates
- Mining controls (start/stop)
- Auto-like functionality
- Ban status checking
- Activity logging
- Device information display

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with the following variables:
   ```
   SECRET_KEY=your_secret_key
   DATABASE_URL=sqlite:///aveum.db
   ```
5. Initialize the database:
   ```bash
   python init_db.py
   ```
6. Run the application:
   ```bash
   python app.py
   ```

## Updating Aveum Credentials

After registering your account, you need to add your Aveum credentials to use the mining and auto-like features. You can do this in two ways:

### Option 1: Using the Web Interface

1. Log in to your account
2. Go to the "Aveum Credentials" page
3. Enter your Aveum email and password
4. Click "Save Credentials"

### Option 2: Using the Command Line Tool

We provide a simple command-line tool to update your Aveum credentials:

#### Windows:
1. Double-click on `update_aveum_credentials.bat`
2. Follow the prompts to enter your registered email and Aveum credentials

#### Linux/Mac:
1. Make the script executable: `chmod +x update_aveum_credentials.sh`
2. Run the script: `./update_aveum_credentials.sh`
3. Follow the prompts to enter your registered email and Aveum credentials

## Deployment on Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Environment Variables:
     - `SECRET_KEY`
     - `DATABASE_URL`

## Usage

1. Register a new account or login
2. Add your Aveum credentials in the settings
3. Use the dashboard to:
   - Start/stop mining
   - Toggle auto-like
   - Check ban status
   - Monitor activity
   - View device information

## API Endpoints

- `/api/status` - Get current status
- `/api/start-mining` - Start mining process
- `/api/stop-mining` - Stop mining process
- `/api/toggle_auto_like` - Toggle auto-like feature
- `/api/check-ban` - Check ban status
- `/api/switch-mode` - Switch between mining and auto-like modes
- `/api/refresh_token` - Refresh Aveum token

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational purposes only. Use at your own risk. Make sure to comply with Aveum's terms of service and API usage guidelines.
# aveumnetwork
