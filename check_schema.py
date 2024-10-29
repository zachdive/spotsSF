import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def check_schema():
    # Load environment variables
    load_dotenv('.env.production')
    database_url = os.getenv('DATABASE_URL')

    # Create SQLAlchemy engine
    engine = create_engine(database_url)

    try:
        with engine.connect() as conn:
            # Check table existence
            tables = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)).fetchall()
            
            print("Available tables:")
            for table in tables:
                print(f"- {table[0]}")
                
            # If workspaces table exists, check its columns
            if any(table[0] == 'workspaces' for table in tables):
                columns = conn.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'workspaces'
                """)).fetchall()
                
                print("\nWorkspaces table columns:")
                for col in columns:
                    print(f"- {col[0]}: {col[1]}")
                
                # Check sample data
                print("\nSample data:")
                rows = conn.execute(text("SELECT * FROM workspaces LIMIT 1")).fetchall()
                if rows:
                    row = dict(rows[0]._mapping)
                    print("First row keys:", list(row.keys()))
                    print("First row values:", list(row.values()))

    except Exception as e:
        print(f"Error checking schema: {e}")

if __name__ == "__main__":
    check_schema()
