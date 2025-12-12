from app import app, db
from models import User, Restaurant, Driver

with app.app_context():
    # Create a test user if not exists
    if not User.query.filter_by(username='testuser').first():
        user = User(username='testuser', password_hash='testpass_hash')
        db.session.add(user)

    # Create a sample restaurant
    if not Restaurant.query.filter_by(name='Demo Restaurant').first():
        rest = Restaurant(name='Demo Restaurant', latitude=38.897676, longitude=-77.036530)
        db.session.add(rest)

    # Create a sample driver
    if not Driver.query.filter_by(name='Demo Driver').first():
        driver = Driver(name='Demo Driver', is_available=True, current_lat=38.900989, current_lon=-77.037415)
        db.session.add(driver)

    db.session.commit()
    print('Seed data inserted (if not already present).')
