import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def setup_database():
    # Load environment variables
    load_dotenv('.env.production')
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("Error: DATABASE_URL not found in environment variables")
        sys.exit(1)

    # Create SQLAlchemy engine
    engine = create_engine(database_url)

    try:
        # Create tables
        with engine.connect() as conn:
            # Create workspaces table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS workspaces (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    address VARCHAR(255) NOT NULL,
                    latitude FLOAT NOT NULL,
                    longitude FLOAT NOT NULL,
                    available_spots INTEGER DEFAULT 0,
                    total_spots INTEGER NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))

            # Insert sample workspace data
            sample_data = [
                ("WeWork Embarcadero Center", "2 Embarcadero Center, San Francisco", 37.7945, -122.3997, 15, 50),
                ("Spaces Mission District", "2323 Mission St, San Francisco", 37.7599, -122.4187, 8, 30),
                ("Workshop Cafe FiDi", "180 Montgomery St, San Francisco", 37.7892, -122.4026, 12, 40)
            ]

            # Check if data already exists
            result = conn.execute(text("SELECT COUNT(*) FROM workspaces")).scalar()

            if result == 0:
                # Insert sample data if table is empty
                for workspace in sample_data:
                    conn.execute(
                        text("""
                            INSERT INTO workspaces (name, address, latitude, longitude, available_spots, total_spots)
                            VALUES (:name, :address, :lat, :lng, :available, :total)
                        """),
                        {
                            "name": workspace[0],
                            "address": workspace[1],
                            "lat": workspace[2],
                            "lng": workspace[3],
                            "available": workspace[4],
                            "total": workspace[5]
                        }
                    )

            conn.commit()

        print("Database setup completed successfully!")

        # Verify data
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM workspaces"))
            rows = [dict(row._mapping) for row in result]
            print("\nCurrent workspaces in database:")
            for row in rows:
                print(f"- {row['name']}: {row['available_spots']}/{row['total_spots']} spots")

    except Exception as e:
        print(f"Error setting up database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database()
