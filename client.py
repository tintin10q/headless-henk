from .brand import send_brand
from .stats import send_getStats
from .get_order import send_getOrder
from .get_capabilities import send_getCapabilities
from .enable_capability import send_enable_capability
from .disable_capability import send_disable_capability
from .get_subscriptions import send_getSubscriptions
from .subscribe import send_subscribe
from .unsubscribe import send_unsubscribe


class Client():
    def __init__(self):
        uri = f"wss://{chief_host}/ws"  # Replace with your server's WebSocket endpoint
        async with websockets.connect(uri) as websocket:
            # Send a sample 'brand' message to the server
            print(type(websocket))
            brand_payload = {
                'author': 'Quinten',
                'name': 'Headless PLACENL Client',
                'version': '1.0'
            }
            await client.send_brand(websocket, **brand_payload)

            # Receive messages from the server
            await receive_messages(websocket)

    async def send_getCapabilities(websocket):
        print("Received get capabilities message")

    async def send_getOrder(websocket):
        # Handle the 'getOrder' message
        # Send the 'order' message with the latest orders
        print("Received 'getOrder' message")

    async def send_getStats(websocket):
        # Handle the 'getStats' message
        # Send the 'stats' message with current server statistics
        print("Received 'getStats' message")

    async def send_unsubscribe(websocket, payload):
        print("got get unsubscribe")

    async def send_subscribe(websocket, payload):
        print("got get subscription message")

    async def send_getSubscriptions(websocket):
        print("get subscriptions")

    async def send_disable_capability(websocket, payload):
        print("disable capability")


# === Add colors.py to path ===
import sys
import os
# Assuming 'colors.py' is located in the same directory as 'side_package'
# If it's in a different location, provide the correct path accordingly.
colors_file_path = os.path.join(os.path.dirname(__file__), '../colors.py')

if colors_file_path not in sys.path:
    sys.path.insert(0, colors_file_path)