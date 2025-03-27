import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        pass  # Можно добавить логику при отключении

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]

        # Отправляем сообщение обратно
        await self.send(text_data=json.dumps({"message": message}))
