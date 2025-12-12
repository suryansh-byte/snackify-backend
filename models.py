from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='customer') # customer, driver, admin
    
class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # Store location as coordinates (crucial for distance calculation)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

class Driver(db.Model):
    __tablename__ = 'drivers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    # Driver's current location (updates via background task/separate driver app)
    current_lat = db.Column(db.Float)
    current_lon = db.Column(db.Float)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=True) # Null until assigned
    
    status = db.Column(db.String(50), default='PENDING') # PENDING, ACCEPTED, PREPARING, OUT_FOR_DELIVERY, DELIVERED
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Delivery Destination Coordinates (from Flutter checkout screen)
    delivery_lat = db.Column(db.Float, nullable=False)
    delivery_lon = db.Column(db.Float, nullable=False)
    
# Menu Items and Order Items tables would be required here too for completeness