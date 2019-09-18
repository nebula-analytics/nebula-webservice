from datetime import datetime, timedelta

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_USERNAME = ''
MONGO_PASSWORD = ''
MONGO_DBNAME = 'nebula'
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
    'joint': joint
}
