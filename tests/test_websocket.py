import pytest
from fastapi.testclient import TestClient
from sf_spots_backend.app import app

def test_websocket_connection():
    """Test WebSocket connection and message broadcasting"""
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        # Test sending and receiving a message
        test_message = "test message"
        websocket.send_text(test_message)
        data = websocket.receive_text()
        assert data == test_message

def test_websocket_multiple_clients():
    """Test WebSocket broadcasting to multiple clients"""
    client1 = TestClient(app)
    client2 = TestClient(app)

    with client1.websocket_connect("/ws") as websocket1:
        with client2.websocket_connect("/ws") as websocket2:
            # Test broadcasting
            test_message = "broadcast test"
            websocket1.send_text(test_message)

            # Both clients should receive the message
            assert websocket1.receive_text() == test_message
            assert websocket2.receive_text() == test_message
