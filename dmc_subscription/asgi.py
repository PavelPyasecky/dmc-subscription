import os

# from ariadne.asgi import GraphQL
# from ariadne.asgi.handlers import GraphQLTransportWSHandler
from django.core.asgi import get_asgi_application

from channels.routing import URLRouter, ProtocolTypeRouter
from django.urls import path

django_asgi_app = get_asgi_application()
from subscription.schema import MyGraphqlWsConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmc_subscription.settings')

# from schemas.schema import schema


application = ProtocolTypeRouter({
    "websocket": URLRouter([
        path("graphql/", MyGraphqlWsConsumer.as_asgi()),
    ])
})

# application = ProtocolTypeRouter(
#     {
#         'http': django_asgi_app,
#         'websocket': URLRouter([
#             path("graphql/", GraphQL(schema=schema, websocket_handler=GraphQLTransportWSHandler())),
#         ])
#     }
# )
