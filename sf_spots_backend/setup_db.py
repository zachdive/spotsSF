import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv('.env.production')

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# Create database engine
engine = create_engine(DATABASE_URL)

def setup_database():
    try:
        # Create workspaces table
        with engine.connect() as conn:
            # Drop existing table first
            conn.execute(text("DROP TABLE IF EXISTS workspaces"))
            conn.commit()
            logger.info("Dropped existing workspaces table if it existed")

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS workspaces (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    address VARCHAR(255) NOT NULL,
                    latitude FLOAT NOT NULL,
                    longitude FLOAT NOT NULL,
                    available_spots INTEGER NOT NULL DEFAULT 0,
                    total_spots INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
            logger.info("Created workspaces table")

            # Insert sample data
            sample_data = [
                ("WeWork Embarcadero Center", "2 Embarcadero Center, San Francisco", 37.7945, -122.3997, 15, 50),
                ("Spaces Mission District", "2323 Mission St, San Francisco", 37.7599, -122.4187, 8, 30),
                ("Workshop Cafe FiDi", "180 Montgomery St, San Francisco", 37.7892, -122.4026, 12, 40)
            ]

            conn.execute(text("""
                INSERT INTO workspaces (name, address, latitude, longitude, available_spots, total_spots)
                VALUES (:name, :address, :latitude, :longitude, :available_spots, :total_spots)
                ON CONFLICT (id) DO NOTHING
            """), [
                {
                    "name": name,
                    "address": address,
                    "latitude": lat,
                    "longitude": lng,
                    "available_spots": available,
                    "total_spots": total
                }
                for name, address, lat, lng, available, total in sample_data
            ])
            conn.commit()
            logger.info("Inserted sample workspace data")

            # Verify data
            result = conn.execute(text("SELECT COUNT(*) FROM workspaces"))
            count = result.scalar()
            logger.info(f"Total workspaces in database: {count}")

    except Exception as e:
        logger.error(f"Database setup failed: {str(e)}")
        raise

if __name__ == "__main__":
    setup_database()
