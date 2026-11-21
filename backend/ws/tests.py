import json
from channels.testing import WebsocketCommunicator
from django.test import TestCase, override_settings
from ws.consumers import PresenceConsumer

TEST_CHANNEL_LAYERS = {'default': {'BACKEND': 'channels.layers.InMemoryChannelLayer'}}


@override_settings(CHANNEL_LAYERS=TEST_CHANNEL_LAYERS)
class MalformedFrameTests(TestCase):
    async def connect(self):
        communicator = WebsocketCommunicator(PresenceConsumer.as_asgi(), '/ws/game/')
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        return communicator

    async def assert_still_alive(self, communicator):
        # an unauthenticated non-auth message makes a live consumer close the socket
        await communicator.send_to(text_data=json.dumps({'type': 'chat_message'}))
        output = await communicator.receive_output()
        self.assertEqual(output['type'], 'websocket.close')

    async def test_invalid_json_does_not_crash_consumer(self):
        communicator = await self.connect()
        await communicator.send_to(text_data='not json')
        await self.assert_still_alive(communicator)

    async def test_binary_frame_does_not_crash_consumer(self):
        communicator = await self.connect()
        await communicator.send_to(bytes_data=b'\x00\x01')
        await self.assert_still_alive(communicator)

    async def test_non_object_json_does_not_crash_consumer(self):
        communicator = await self.connect()
        await communicator.send_to(text_data='[]')
        await self.assert_still_alive(communicator)
