import os
from datetime import datetime, timedelta

_host = os.getenv("mongo_host", "localhost")
_host_port = int(os.getenv("mongo_port", "27017"))
_host_username = os.getenv("mongo_user", "")
_host_password = os.getenv("mongo_pass", "")
_host_dbname = 'nebula'

_host_login_str = f"{_host_username}:{_host_password}@" if _host_username or _host_password else ""
MONGO_URI = f"mongodb://{_host_login_str}{_host}:{_host_port}"

RESOURCE_METHODS = ['GET']
view_collection_name = "views"
book_collection_name = "books"

PAGINATION = False

# MongoDB Query to get the most recent 30mins of data.
# db.views.find({at: {$gt: (new Date(ISODate().getTime() - 1000*60*30))  }},{at:1, _id:0})

joint = {
    'datasource': {
        'source': view_collection_name,
        'aggregation': {
            'pipeline': [
                {"$match": {"at": {"$gte": datetime.now() - timedelta(minutes=30)}}},
                {"$group": {"_id": "$doc_id", "count": {"$sum": 1}, "last_viewed": {"$max": "$at"}}},
                {"$lookup": {
                    "from": book_collection_name,
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

