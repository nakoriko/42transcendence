#importa classe base per consumer
from channels.generic.websocket import WebsocketConsumer

#eredita da classe base e cambia alcuni metodi
class EchoConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()#accetta a priori, aggiungere controllo jwt

    def disconnect(self, close_code):
        pass#non fare niente, poi cambiare

    def receive(self, text_data):
        self.send(text_data=text_data)