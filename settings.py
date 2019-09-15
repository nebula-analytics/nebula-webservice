# import os

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_USERNAME = ''
MONGO_PASSWORD = ''
MONGO_DBNAME = 'nebula'
RESOURCE_METHODS = ['GET']

PAGINATION = False

# books = {
# 	'schema': {
# 		'title': {
# 			'type': 'string'
# 		}
# 	}
# }

# views = {
# 	'schema': {
# 		'doc_id': {
# 			'type': 'string'
# 		}
# 	}
# }

joint = {
	'datasource':{
		'source' : 'views',
		'aggregation': {
			'pipeline': [
				{"$group": {"_id": "$doc_id", "count": {"$sum": 1}, "last_viewed": {"$max": "$at"}}},
                         {"$lookup": {
                             "from": "books",
                             "localField": "_id",
                             "foreignField": "doc_id",
                             "as": "matched"
                         }},

                         {"$unwind": "$matched"},
                         {"$addFields": {"matched.count": "$count", "matched.last_view": "$last_viewed"}},
                         {"$replaceRoot": {"newRoot": "$matched"}},
                         {"$project": {
                             "doc_id": "$id",
                             "title": "$title",
                             "identifiers": "$identifier",
                             "language": "$lang3",
                             "record_type": "$_type",
                             "extra_fields": "$extra_fields",
                             "count": "$count",
                             "last_view": "$last_view"
                         }}
			]
		}
	}
}


DOMAIN = {
	# 'books': books,
	# 'views': views,
	'joint': joint
}



