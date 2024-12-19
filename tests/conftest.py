import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

@pytest.fixture
def test_db():
    """Create a test database in memory"""
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create test tables
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE workspaces (
                id INTEGER PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                address VARCHAR(255) NOT NULL,
                latitude FLOAT NOT NULL,
                longitude FLOAT NOT NULL,
                available_spots INTEGER DEFAULT 0,
                total_spots INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Insert test data
        conn.execute(text("""
            INSERT INTO workspaces (name, address, latitude, longitude, available_spots, total_spots)
            VALUES ('Test Space', '123 Test St', 37.7749, -122.4194, 10, 20)
        """))
        conn.commit()

    yield engine

    # Cleanup (SQLite in-memory DB is automatically cleaned up)
