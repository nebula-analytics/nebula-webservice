from datetime import datetime, timedelta

from eve import Eve
from flask.json import jsonify
from flask_cors import CORS

from utils.ConfigMap import ConfigMap, add_discovery_path

add_discovery_path("./eve.config.yaml")
config = ConfigMap.get_singleton().eve.dict

"""
We need to override the domain otherwise we can't pass a datetime
"""
print(config)
config["DOMAIN"]["joint"] = {
    'datasource': {
        'source': "views",
        'aggregation': {
            'pipeline': [
                {"$match": {"at": {"$gte": datetime.now() - timedelta(minutes=30)}}},
                # {"$match": "$where$"},
                {"$group": {"_id": "$doc_id", "count": {"$sum": 1}, "last_viewed": {"$max": "$at"}}},
                {"$lookup": {
                    "from": "books",
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
                    "last_view": "$last_view",
                    "links": "$extra_fields.delivery.link"
                }},
                {"$sort": {"last_view": -1, "title": -1, "doc_id": -1}}
            ]
        }
    }
}

app = Eve(settings=config)
CORS(app)


@app.route("/application/config")
def get_config():
    return jsonify(ConfigMap.theme)


if __name__ == '__main__':
    app.run(host="0.0.0.0")
