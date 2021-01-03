from django.urls import path

from .consumers import FeedConsumer

websocket_urlpatterns = [
    path('ws/owned/<biz_slug>/feed/', FeedConsumer.as_asgi())
]
