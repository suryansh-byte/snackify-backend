"""
Simple seed script for MongoDB when `MONGODB_URI` is configured.
Run: `python seed_mongo.py` or run inside the virtualenv where requirements are installed.
It will insert example `users`, `restaurants`, and `drivers` documents into the
configured MongoDB database.
"""
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from flask_bcrypt import generate_password_hash

MONGODB_URI = os.environ.get('MONGODB_URI')
if not MONGODB_URI:
    print('MONGODB_URI not set in environment. Aborting.')
    exit(1)

try:
    client = MongoClient(MONGODB_URI)
    db = None
    try:
        db = client.get_default_database()
    except Exception:
        db = client.get_database('snackify')

    users = db.get_collection('users')
    restaurants = db.get_collection('restaurants')
    drivers = db.get_collection('drivers')

    # Insert sample user
    if users.count_documents({'username': 'demo'}, limit=1) == 0:
        users.insert_one({
            'username': 'demo',
            'password_hash': generate_password_hash('password').decode('utf-8')
        })
        print('Inserted demo user')
    else:
        print('Demo user already present')

    # Insert sample restaurant
    if restaurants.count_documents({'name': 'Demo Bites'}, limit=1) == 0:
        restaurants.insert_one({
            'name': 'Demo Bites',
            'latitude': 38.8977,
            'longitude': -77.0365,
            'address': '1600 Pennsylvania Ave NW, Washington, DC 20500'
        })
        print('Inserted demo restaurant')
    else:
        print('Demo restaurant already present')

    # Insert sample driver
    if drivers.count_documents({'name': 'Driver One'}, limit=1) == 0:
        drivers.insert_one({
            'name': 'Driver One',
            'current_lat': 38.900,
            'current_lon': -77.037,
            'is_available': True
        })
        print('Inserted demo driver')
    else:
        print('Demo driver already present')

    print('MongoDB seeding complete')

except PyMongoError as e:
    print('Failed to seed MongoDB:', e)
    exit(1)
*** End Patch