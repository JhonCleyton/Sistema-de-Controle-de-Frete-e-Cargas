from app import app, db, initialize_database

with app.app_context():
    # Drop all tables
    db.drop_all()
    
    # Initialize database
    initialize_database()
