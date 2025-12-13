from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from haversine import haversine_distance
from models import db, User, Restaurant, Driver, Order
# Optional MongoDB support (PyMongo)
from pymongo import MongoClient, errors as pymongo_errors
import jwt
import datetime
import os
import requests # Used for geocoding
from flask_cors import CORS

# --- CONFIGURATION ---
app = Flask(__name__)
# Enable CORS so the Flutter app (emulator/device) can access the API during development
CORS(app)
# Default to a local SQLite DB for quick local testing. Override with DATABASE_URL env var for production.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///snackify.db')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_ultra_secret_key') # Used for JWT
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)

# Optional MongoDB client. If `MONGODB_URI` is set in environment, the app
# will attempt to connect and expose a `/mongo-health` endpoint to verify
# connectivity. This keeps the existing SQLAlchemy code intact while
# providing an alternate backend connection for services that prefer MongoDB.
MONGO_CLIENT = None
MONGO_DB = None
MONGODB_URI = os.environ.get('MONGODB_URI')
if MONGODB_URI:
    try:
        MONGO_CLIENT = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        # Try a quick ping to verify connection
        MONGO_CLIENT.admin.command('ping')
        # If the URI contains a default database, get_default_database() returns it.
        try:
            MONGO_DB = MONGO_CLIENT.get_default_database()
        except Exception:
            # Fallback: use a database named 'snackify'
            MONGO_DB = MONGO_CLIENT.get_database('snackify')
        app.logger.info('Connected to MongoDB')
    except pymongo_errors.PyMongoError as e:
        MONGO_CLIENT = None
        MONGO_DB = None
        app.logger.error(f'Failed to connect to MongoDB: {e}')

# --- HELPER FUNCTION: AUTHENTICATION DECORATOR ---
# This ensures only authenticated users can access certain routes
def token_required(f):
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except Exception as e:
            return jsonify({'message': f'Token is invalid or expired! {e}'}), 401

        return f(current_user, *args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated

# --- CORE ROUTES ---

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    new_user = User(username=data['username'], password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully!'}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    auth = request.get_json()
    user = User.query.filter_by(username=auth['username']).first()

    if user and bcrypt.check_password_hash(user.password_hash, auth['password']):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24) # Token expires in 24h
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({'token': token}), 200

    return jsonify({'message': 'Invalid credentials'}), 401


# --- DSA HIGHLIGHT: DRIVER ASSIGNMENT ---

def assign_nearest_driver(restaurant_id):
    """
    Implements the Nearest Neighbor (Greedy) Algorithm using Haversine distance.
    """
    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return None, "Restaurant not found"
        
    available_drivers = Driver.query.filter_by(is_available=True).all()
    
    nearest_driver = None
    min_distance = float('inf')
    
    # Nearest Neighbor Algorithm Loop
    for driver in available_drivers:
        # Skip driver if they don't have location data
        if driver.current_lat is None or driver.current_lon is None:
            continue
            
        # 1. Calculate distance using Haversine
        distance = haversine_distance(
            restaurant.latitude, restaurant.longitude, 
            driver.current_lat, driver.current_lon
        )
        
        # 2. Check for minimum distance (Greedy Choice)
        if distance < min_distance:
            min_distance = distance
            nearest_driver = driver
            
    return nearest_driver, min_distance

@app.route('/api/orders/place', methods=['POST'])
@token_required
def place_order(current_user):
    data = request.get_json()
    
    # --- Geocoding Simulation (Replace with Google Maps API call) ---
    # For a real project, you would call a geocoding API here to convert 
    # the address string into delivery_lat and delivery_lon.
    # We will use mock coordinates for now.
    mock_delivery_lat = 38.900989
    mock_delivery_lon = -77.037415

    # 1. Create the Order
    new_order = Order(
        user_id=current_user.id,
        restaurant_id=data['restaurant_id'], # Passed from Flutter
        total_price=data['total_price'],     # Calculated in Flutter, validated/recalculated here
        delivery_lat=mock_delivery_lat,
        delivery_lon=mock_delivery_lon
    )
    db.session.add(new_order)
    db.session.commit()
    
    # 2. Automatically attempt to assign driver when order is placed
    nearest_driver, distance = assign_nearest_driver(data['restaurant_id'])
    
    if nearest_driver:
        new_order.driver_id = nearest_driver.id
        new_order.status = 'ACCEPTED' # Move to ACCEPTED once driver is assigned
        db.session.commit()
        # ** Here is where you would trigger the WebSocket notification **
        # socketio.emit('order_assigned', {'order_id': new_order.id, 'driver_name': nearest_driver.name})
    else:
        # If no driver is found, status remains PENDING or needs manual review
        new_order.status = 'PENDING_DRIVER'
        db.session.commit()
        
    return jsonify({
        'message': 'Order placed successfully', 
        'order_id': new_order.id,
        'driver_assigned': nearest_driver.name if nearest_driver else 'None',
        'distance_to_pickup': f"{distance:.2f} km" if nearest_driver else 'N/A'
    }), 201


@app.route('/api/orders/<int:order_id>', methods=['GET'])
@token_required
def get_order_status(current_user, order_id):
    order = Order.query.get(order_id)
    
    if not order or order.user_id != current_user.id:
        return jsonify({'message': 'Order not found or unauthorized'}), 404
        
    driver_name = Driver.query.get(order.driver_id).name if order.driver_id else 'N/A'
    
    return jsonify({
        'order_id': order.id,
        'status': order.status,
        'driver_name': driver_name,
        # Flutter needs these for map tracking (Step 5)
        'delivery_lat': order.delivery_lat,
        'delivery_lon': order.delivery_lon,
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200


@app.route('/mongo-health', methods=['GET'])
def mongo_health():
    """Lightweight endpoint to check MongoDB connectivity when `MONGODB_URI` is used.
    Returns list of databases when reachable, otherwise returns an error message.
    """
    if not MONGO_CLIENT:
        return jsonify({'status': 'mongo_disabled', 'message': 'MONGODB_URI not configured or connection failed'}), 400

    try:
        # server_info or list_database_names will raise if the server is unreachable
        dbs = MONGO_CLIENT.list_database_names()
        return jsonify({'status': 'ok', 'dbs': dbs}), 200
    except pymongo_errors.PyMongoError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    # Initialize the database and create tables if they don't exist
    with app.app_context():
        db.create_all()

    # ** You would replace app.run(debug=True) with socketio.run(app, debug=True)
    #    when integrating WebSockets (Flask-SocketIO) in Step 5. **
    app.run(debug=True)