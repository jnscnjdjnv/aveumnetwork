# Aveum Mining Dashboard

A Flask-based web application for managing Aveum mining and auto-like operations.

## Features

- **Account Management**
  - User authentication
  - Aveum credentials management
  - Device information tracking

- **Mining Operations**
  - Start/Stop mining
  - Real-time mining status
  - Mining rewards tracking
  - Mining session statistics

- **Auto-Like System**
  - Toggle auto-like functionality
  - Like statistics tracking
  - Error monitoring

- **Status Monitoring**
  - Ban status checking
  - Activity logging
  - Real-time status updates

## Prerequisites

- Python 3.8 or higher
- Flask
- SQLAlchemy
- aiohttp
- Other dependencies listed in requirements.txt

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/aveum-mining-dashboard.git
cd aveum-mining-dashboard
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your Aveum credentials:
```
AVEUM_EMAIL=your_email@example.com
AVEUM_PASSWORD=your_password
```

5. Initialize the database:
```bash
flask db upgrade
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Access the dashboard at `http://localhost:5000`

3. Log in with your credentials

4. Configure your Aveum credentials in the settings

5. Start mining or auto-like operations from the dashboard

## Project Structure

```
aveum-mining-dashboard/
├── app.py                 # Main application file
├── aveum_api.py          # Aveum API integration
├── models.py             # Database models
├── requirements.txt      # Project dependencies
├── static/              # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── dashboard.js
│       └── main.js
└── templates/           # HTML templates
    ├── base.html
    ├── dashboard.html
    ├── login.html
    └── register.html
```

## API Endpoints

- `/api/status` - Get current status
- `/api/start-mining` - Start mining operation
- `/api/stop-mining` - Stop mining operation
- `/api/toggle_auto_like` - Toggle auto-like feature
- `/api/check-ban` - Check ban status
- `/api/refresh_token` - Refresh Aveum token
- `/api/switch-mode` - Switch between mining and auto-like modes

## Security Considerations

- Store sensitive credentials in `.env` file
- Use HTTPS in production
- Implement rate limiting
- Regular token refresh
- Monitor for suspicious activities

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
