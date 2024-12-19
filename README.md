# SF Spots Backend

FastAPI backend for the SF Spots application. Provides workspace information and real-time occupancy updates.

## Features
- Workspace listing and details
- Real-time occupancy updates via WebSocket
- PostgreSQL database integration
- Automated test suite with pytest
- API documentation with Swagger UI

## Development Setup
1. Clone the repository
```bash
git clone https://github.com/zachdive/spotsSF.git
cd spotsSF
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables
```bash
export DATABASE_URL=postgresql://user:password@localhost:5432/sf_spots_db
```

## Running Tests
The project uses pytest for testing. To run the tests:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=sf_spots_backend
```

## API Documentation
The API documentation is available at `/docs` when running the server. Main endpoints:

### REST Endpoints
- `GET /healthz` - Health check endpoint
- `GET /workspaces` - List all workspaces
- `GET /workspace/{workspace_id}/occupancy` - Get workspace occupancy

### WebSocket Endpoint
- `WebSocket /ws/{workspace_id}` - Real-time workspace updates

WebSocket message format:
```json
{
  "workspace_id": 1,
  "available_spots": 5
}
```

## Deployment
The application is configured for deployment on Render.com:

1. Fork the repository
2. Create a new Web Service on Render
3. Connect your repository
4. Use the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn sf_spots_backend.app:app --host 0.0.0.0 --port $PORT`
   - Environment Variables:
     - `DATABASE_URL`: Your PostgreSQL connection string
     - `PYTHON_VERSION`: 3.12.0

The deployment configuration is defined in `render.yaml`.

## Database Schema
The database uses PostgreSQL with the following schema:

```sql
CREATE TABLE workspaces (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    available_spots INTEGER NOT NULL,
    total_spots INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Contributing
1. Create a feature branch
2. Make your changes
3. Add tests for new functionality
4. Create a pull request

Please ensure all tests pass before submitting a pull request.
