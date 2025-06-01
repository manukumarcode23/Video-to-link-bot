import re
from os import environ

id_pattern = re.compile(r'^.\d+$')

# Bot information
SESSION = environ.get('SESSION', 'TechVJBot')
API_ID = int(environ.get('API_ID', '25929889'))
API_HASH = environ.get('API_HASH', 'fd980dbd069e0b45d0dec91f7e616bad')
BOT_TOKEN = environ.get('8033229577:AAGlmDiXoXWhdkhcbidYnJUILbK-7kCaE0k', "")

# Bot settings
PORT = environ.get("PORT", "8080")

# Online Stream and Download
MULTI_CLIENT = False
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))  # 20 minutes
if 'DYNO' in environ:
    ON_HEROKU = True
else:
    ON_HEROKU = False
URL = environ.get("URL", "")

# Admins, Channels & Users
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1002619435151'))
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '5456381819').split()]

# MongoDB information
DATABASE_URI = environ.get('DATABASE_URI', "mongodb+srv://ammumanu:ammumanu@ammumanu.qnr5e.mongodb.net/?retryWrites=true&w=majority&appName=ammumanu")
DATABASE_NAME = environ.get('DATABASE_NAME', "ammumanu")

# Shortlink Info
SHORTLINK = bool(environ.get('SHORTLINK', True))  # Set True Or False
SHORTLINK_URL = environ.get('SHORTLINK_URL', 'api.shareus.io')
SHORTLINK_API = environ.get('SHORTLINK_API', 'hRPS5vvZc0OGOEUQJMJzPiojoVK2')