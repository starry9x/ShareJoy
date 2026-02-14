from app import app, db
from users import User
from reports import Report

with app.app_context():
    print("Starting database migration...")
    
    # Add new columns to user table
    try:
        print("\n1. Adding user_unique_id column...")
        db.session.execute(db.text('ALTER TABLE user ADD COLUMN user_unique_id VARCHAR(10)'))
        db.session.commit()
        print("✅ user_unique_id column added!")
    except Exception as e:
        print(f"⚠️ user_unique_id column might already exist: {e}")
        db.session.rollback()
    
    try:
        print("\n2. Adding activities_created_count column...")
        db.session.execute(db.text('ALTER TABLE user ADD COLUMN activities_created_count INTEGER DEFAULT 0'))
        db.session.commit()
        print("✅ activities_created_count column added!")
    except Exception as e:
        print(f"⚠️ activities_created_count column might already exist: {e}")
        db.session.rollback()
    
    try:
        print("\n3. Adding first_activity_completed column...")
        db.session.execute(db.text('ALTER TABLE user ADD COLUMN first_activity_completed BOOLEAN DEFAULT 0'))
        db.session.commit()
        print("✅ first_activity_completed column added!")
    except Exception as e:
        print(f"⚠️ first_activity_completed column might already exist: {e}")
        db.session.rollback()
    
    # Create reports table
    try:
        print("\n4. Creating reports table...")
        db.create_all()
        print("✅ Reports table created!")
    except Exception as e:
        print(f"⚠️ Reports table might already exist: {e}")
        db.session.rollback()
    
    # Generate unique IDs for existing users
    print("\n5. Generating unique IDs for existing users...")
    users = User.query.all()
    for user in users:
        if not user.user_unique_id:
            user.user_unique_id = User.generate_unique_id()
            print(f"   Generated ID for {user.full_name}: {user.user_unique_id}")
        if user.activities_created_count is None:
            user.activities_created_count = 0
        if user.first_activity_completed is None:
            user.first_activity_completed = False
    
    db.session.commit()
    print(f"\n✅ Migration complete! Updated {len(users)} users.")
    
    # Verify migration
    print("\n6. Verifying migration...")
    test_user = User.query.first()
    if test_user:
        print(f"   Sample user: {test_user.full_name}")
        print(f"   - Unique ID: {test_user.user_unique_id}")
        print(f"   - Activities Count: {test_user.activities_created_count}")
        print(f"   - First Activity: {test_user.first_activity_completed}")
    
    print("\n🎉 All done! Database is ready to use.")