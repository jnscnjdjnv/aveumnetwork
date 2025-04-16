import os
import random
import secrets
import aiohttp
import asyncio
from datetime import datetime

# Constants
API_BASE_URL = 'https://api.aveum.io'
API_ENDPOINTS = {
    'login': '/users/login',
    'startHub': '/users/start-hub',
    'stopHub': '/users/stop-hub',
    'hubStatus': '/users/hub-status',
    'profile': '/users/profile',
    'checkBan': '/users/check-ban',
    'claimReward': '/users/claim-reward',
    'discoverFeed': '/users/discover-feed',
    'discoverOnlineUsers': '/users/discover-online-users',
    'toggleLike': '/users/toggle-like/'
}

ANDROID_DEVICE_MODELS = [
    'SM-G9750', 'SM-G988B', 'SM-G973F', 'SM-G975F', 'SM-N975F',
    'SM-A515F', 'SM-A715F', 'SM-A516B', 'SM-A526B', 'SM-A536E',
    'Pixel 6', 'Pixel 6 Pro', 'Pixel 7', 'Pixel 7 Pro', 'Pixel 8',
    'OnePlus 9', 'OnePlus 10 Pro', 'OnePlus 11', 'OnePlus Nord 3',
    'Redmi Note 12', 'Redmi Note 11', 'POCO F5', 'POCO X5 Pro',
    'Vivo X90', 'Vivo V25', 'Vivo Y35', 'Oppo Reno 8', 'Oppo Find X5'
]

ANDROID_VERSIONS = ['10', '11', '12', '13']

# Helper functions
def generate_random_device_id():
    return secrets.token_hex(8)

def get_random_device_model():
    return random.choice(ANDROID_DEVICE_MODELS)

def get_random_android_version():
    return random.choice(ANDROID_VERSIONS)

def get_random_delay(min_val, max_val):
    return random.randint(min_val, max_val)

def get_headers(token=None):
    headers = {
        'User-Agent': 'okhttp/4.9.2',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip',
        'Content-Type': 'application/json'
    }
    
    if token:
        headers['authorization'] = f'Bearer {token}'
    
    return headers

def get_login_payload(email, password):
    device_id = generate_random_device_id()
    device_model = get_random_device_model()
    platform_version = get_random_android_version()
    
    return {
        'email': email,
        'password': password,
        'language': "en",
        'device_id': device_id,
        'device_model': device_model,
        'platform': "android",
        'platform_version': platform_version,
        'version': "1.0.25",
        'ip_address': "180.249.164.195"
    }

# API functions
async def login(email, password):
    try:
        payload = get_login_payload(email, password)
        headers = get_headers()
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_BASE_URL}{API_ENDPOINTS['login']}", 
                json=payload, 
                headers=headers
            ) as response:
                data = await response.json()
                if 'token' in data:
                    return {
                        'success': True,
                        'token': data['token'],
                        'device_id': payload['device_id'],
                        'device_model': payload['device_model'],
                        'platform_version': payload['platform_version']
                    }
                else:
                    error_message = data.get('message', 'Login failed')
                    if isinstance(error_message, dict):
                        error_message = error_message.get('error', 'Login failed')
                    return {
                        'success': False,
                        'error': error_message
                    }
    except Exception as error:
        return {
            'success': False,
            'error': str(error)
        }

async def get_user_profile(token):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_BASE_URL}{API_ENDPOINTS['profile']}", 
                headers=get_headers(token)
            ) as response:
                data = await response.json()
                return {
                    'success': True,
                    'data': data
                }
    except Exception as error:
        return {
            'success': False,
            'error': str(error)
        }

async def check_user_ban(token):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_BASE_URL}{API_ENDPOINTS['checkBan']}", 
                headers=get_headers(token)
            ) as response:
                data = await response.json()
                return {
                    'success': True,
                    'data': data
                }
    except Exception as error:
        return {
            'success': False,
            'error': str(error)
        }

async def start_hub_mining(token):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_BASE_URL}{API_ENDPOINTS['startHub']}", 
                json={}, 
                headers=get_headers(token)
            ) as response:
                data = await response.json()
                return {
                    'success': True,
                    'data': data
                }
    except Exception as error:
        return {
            'success': False,
            'error': str(error)
        }

async def stop_hub_mining(token):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_BASE_URL}{API_ENDPOINTS['stopHub']}", 
                json={}, 
                headers=get_headers(token)
            ) as response:
                data = await response.json()
                return {
                    'success': True,
                    'data': data
                }
    except Exception as error:
        return {
            'success': False,
            'error': str(error)
        }

async def get_hub_status(token):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_BASE_URL}{API_ENDPOINTS['hubStatus']}", 
                headers=get_headers(token)
            ) as response:
                data = await response.json()
                return {
                    'success': True,
                    'data': data
                }
    except Exception as error:
        return {
            'success': False,
            'error': str(error)
        }

async def claim_reward(token):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_BASE_URL}{API_ENDPOINTS['claimReward']}", 
                json={}, 
                headers=get_headers(token)
            ) as response:
                data = await response.json()
                return {
                    'success': True,
                    'data': data
                }
    except Exception as error:
        return {
            'success': False,
            'error': str(error)
        }

async def get_discover_feed(token, page=1, limit=20):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_BASE_URL}{API_ENDPOINTS['discoverFeed']}?page={page}&limit={limit}", 
                headers=get_headers(token)
            ) as response:
                data = await response.json()
                return {
                    'success': True,
                    'data': data
                }
    except Exception as error:
        return {
            'success': False,
            'error': str(error)
        }

async def get_discover_online_users(token, page=1, limit=20):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_BASE_URL}{API_ENDPOINTS['discoverOnlineUsers']}?page={page}&limit={limit}", 
                headers=get_headers(token)
            ) as response:
                data = await response.json()
                return {
                    'success': True,
                    'data': data
                }
    except Exception as error:
        return {
            'success': False,
            'error': str(error)
        }

async def toggle_like(token, user_id):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_BASE_URL}{API_ENDPOINTS['toggleLike']}{user_id}", 
                json={}, 
                headers=get_headers(token)
            ) as response:
                data = await response.json()
                return {
                    'success': True,
                    'data': data
                }
    except Exception as error:
        return {
            'success': False,
            'error': str(error)
        } 