import os

from channels.routing import ProtocolTypeRouter,URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mySite.settings')

django_asgi_app = get_asgi_application()
from ApiMonitoring import routing

# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     "websocket" : AllowedHostsOriginValidator(
#         URLRouter(
#             routing.websocket_urlpatterns
#         )
#     )
# })