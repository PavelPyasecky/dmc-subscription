import channels_graphql_ws
import graphene
from graphene import relay
from graphene_django import DjangoObjectType

from subscription import models


class SpareNode(DjangoObjectType):
    class Meta:
        model = models.Spares
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
        }
        interfaces = (relay.Node,)


class MySubscription(
    channels_graphql_ws.Subscription
):
    """Simple GraphQL subscription."""

    # Leave only latest 64 messages in the server queue.
    # notification_queue_limit = 64

    # Subscription payload.
    spare = graphene.Field(SpareNode)

    @staticmethod
    def subscribe(root, info):
        """Called when user subscribes."""

        # Return the list of subscription group names.
        return ["group42"]

    @staticmethod
    def publish(payload, info):
        """Called to notify the client."""

        # Here `payload` contains the `payload` from the `broadcast()`
        # invocation (see below). You can return `None` if you wish to
        # suppress the notification to a particular client. For example,
        # this allows to avoid notifications for the actions made by
        # this particular client.

        spare = models.Spares.objects.select_related('created_by').latest('created_date')

        return MySubscription(spare=spare)


class Query(graphene.ObjectType):
    """Root GraphQL query."""
    # Graphene requires at least one field to be present. Check
    # Graphene docs to see how to define queries.
    value = graphene.String()

    async def resolve_value(self):
        return "test"


class Mutation(graphene.ObjectType):
    """Root GraphQL mutation."""
    # Check Graphene docs to see how to define mutations.
    pass


class Subscription(graphene.ObjectType):
    """Root GraphQL subscription."""
    my_subscription = MySubscription.Field()


graphql_schema = graphene.Schema(
    query=Query,
    subscription=Subscription,
)


class MyGraphqlWsConsumer(channels_graphql_ws.GraphqlWsConsumer):
    """Channels WebSocket consumer which provides GraphQL API."""
    schema = graphql_schema

    channel_name = 'default'

    # Uncomment to send ping message every 42 seconds.
    # send_ping_every = 42

    # Uncomment to process requests sequentially (useful for tests).
    # strict_ordering = True

    async def on_connect(self, payload):
        """New client connection handler."""
        # You can `raise` from here to reject the connection.
        print("New client connected!")

