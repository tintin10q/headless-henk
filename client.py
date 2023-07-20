print("Starting client")

import asyncio
import websockets
import json

from handelers import *
from colors import *

async def handle_client(websocket, path):
    async for message in websocket:
        try:
            data = json.loads(message)
            if 'type' not in data:
                return await send_error(websocket, 'invalidPayload', 'noType')
            message_type = data['type']
            match message_type:
                case 'pong':
                    await handle_pong(websocket)
                case 'brand':
                    await handle_brand(websocket, data.get('payload'))
                case 'getOrder':
                    await handle_get_order(websocket)
                case 'getStats':
                    await handle_get_stats(websocket)
                case 'getCapabilities':
                    await handle_get_capabilities(websocket)
                case 'enableCapability':
                    await handle_enable_capability(websocket, data.get('payload'))
                case 'disableCapability':
                    await handle_disable_capability(websocket, data.get('payload'))
                case 'getSubscriptions':
                    await handle_get_subscriptions(websocket)
                case 'subscribe':
                    await handle_subscribe(websocket, data.get('payload'))
                case 'unsubscribe':
                    await handle_unsubscribe(websocket, data.get('payload'))
                case _:
                    await send_error(websocket, 'invalidPayload', 'unknownType')
        except json.JSONDecodeError:
            await send_error(websocket, 'invalidMessage', 'failedToParseJSON')
        except Exception as e:
            print(f"Error processing message: {e}")
            await send_error(websocket, 'unknownError', str(e))

async def handle_pong(websocket):
    # Handle the 'pong' message
    # Reset keepalive timer, if needed
    print("Received 'pong' message")


async def send_error(websocket, error_type, error_detail):
    error_message = {
        'type': 'error',
        'payload': {
            'type': error_type,
            'detail': error_detail
        }
    }
    await websocket.send(json.dumps(error_message))

async def start_server():
    from config import ip, port
    server = await websockets.serve(handle_client, ip, port)

    print(f"Server started on {PURPLE}{ip}{RESET}:{GREEN}{port}{RESET}")
    await server.wait_closed()

def start():
    asyncio.get_event_loop().run_until_complete(start_server())

if __name__ == '__main__':
    start()
