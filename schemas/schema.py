import asyncio
import json
from datetime import datetime

# from ariadne import MutationType, SubscriptionType, make_executable_schema, QueryType
from channels.db import database_sync_to_async

from subscription import models

type_defs = """
  type User {
    id: Int
    username: String
    email: String
  }

  type Spare {
    id: Int
    name: String
    count: Int
    cost: Int
    createdDate: String
    createdBy: User
  }

  input SpareInput {
    name: String!
    count: Int!
    cost: Int!
  }

  type Query{
    getSpares: [Spare]
  }

  type Mutation{
    createSpare(input: SpareInput): Spare
  }

  type Subscription {
    getLatestSpare: Spare
  }
"""

query = QueryType()


def resolve_get_spares(*_):
    spares = models.Spares.objects.all()
    return {
        "spares": spares
    }


query.set_field('getSpares', resolve_get_spares)

mutation = MutationType()


@database_sync_to_async
def resolve_create_spare(*_, input: dict):
    timestamp = datetime.utcnow()
    spare = models.Spares.objects.create(**input, created_date=timestamp, created_by_id=1, updated_by_id=1,
                                         updated_date=timestamp)
    spare.save()
    return spare


mutation.set_field('createSpare', resolve_create_spare)

subscription = SubscriptionType()


@subscription.source("getLatestSpare")
async def latest_spare_generator(_, info):
    while True:
        await asyncio.sleep(1)
        # wrapping Django ORM synchronous operation (Blog.objects.latest("title")) with
        # database_sync_to_async method to be executed in an asynchronous environment
        spare = await database_sync_to_async(models.Spares.objects.select_related('created_by').latest)('created_date')

        spare.createdDate = spare.created_date
        spare.createdBy = spare.created_by
        response = spare.__dict__
        yield response


async def resolve_get_latest_spare(response, obj):
    return response


subscription.set_source('getLatestSpare', latest_spare_generator)
subscription.set_field('getLatestSpare', resolve_get_latest_spare)

schema = make_executable_schema(type_defs, mutation, query, subscription)
