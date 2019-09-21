import os
from datetime import datetime, timedelta

_DB_HOST = os.getenv("mongo_host", "localhost")
_DB_PORT = int(os.getenv("mongo_port", "27017"))
_DB_USERNAME = os.getenv("mongo_user", "")
_DB_PASSWORD = os.getenv("mongo_pass", "")
_DB_DBNAME = 'nebula'

LOGIN_STR = f"{_DB_USERNAME}:{_DB_PASSWORD}@" if _DB_USERNAME or _DB_PASSWORD else ""
MONGO_URI = f"mongodb://{LOGIN_STR}{_DB_HOST}:{_DB_PORT}"

RESOURCE_METHODS = ['GET']
VIEW_COLLECTION = "views"
BOOK_COLLECTION = "books"

PAGINATION = False

# MongoDB Query to get the most recent 30mins of data.
# db.views.find({at: {$gt: (new Date(ISODate().getTime() - 1000*60*30))  }},{at:1, _id:0})

joint = {
    'datasource': {
        'source': VIEW_COLLECTION,
        'aggregation': {
            'pipeline': [
                {"$match": {"at": {"$gte": datetime.now() - timedelta(minutes=30)}}},
                {"$group": {"_id": "$doc_id", "count": {"$sum": 1}, "last_viewed": {"$max": "$at"}}},
                {"$lookup": {
                    "from": BOOK_COLLECTION,
                    "localField": "_id",
                    "foreignField": "doc_id",
                    "as": "matched"
                }},
                {"$match": {"matched": {"$not": {"$eq": []}}}},
                {"$match": {"matched.status": {"$eq": "processed"}}},
                {"$unwind": "$matched"},
                {"$addFields": {"matched.count": "$count", "matched.last_view": "$last_viewed"}},
                {"$replaceRoot": {"newRoot": "$matched"}},
                {"$project": {
                    "doc_id": "$doc_id",
                    "title": "$title",
                    "identifiers": "$identifier",
                    "language": "$lang3",
                    "record_type": "$_type",
                    "extra_fields": "$extra_fields",
                    "count": "$count",
                    "last_view": "$last_view"
                }},
                {"$sort": {"last_view": -1}}
            ]
        }
    }
}

DOMAIN = {
    'joint': joint,
    'views': {},
    'books': {},
}

