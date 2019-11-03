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
""" TODO: REMOVE ASAP """
config["DOMAIN"]["joint"] = {
    'datasource': {
        'source': "views",
        'aggregation': {
            'options': {
                "allowDiskUse": True
            },
            'pipeline': [
                {"$match": {"at": {"$gte": datetime.now() - timedelta(minutes=30)}}},
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


def clean_bad_dates(values: list):
    new_value = []
    for value in values:
        if "$gte" in value["at"]:
            key = "$gte"
        else:
            key = "$lte"
        try:
            """Validate date value and convert to mongo-friendly"""
            # actual_value = parse(value["at"][key])
            actual_value = datetime.fromisoformat(value["at"][key])
            value["at"][key] = actual_value
            new_value.append(value)
        except (ValueError, TypeError):
            pass
    values.clear()
    values.extend(new_value)


def set_default_times(values: list):
    default_window = timedelta(minutes=30)
    if not values:
        values.append({"at": {"$gte": (datetime.utcnow() - default_window)}})
    if len(values) == 1:
        value = values[0]["at"]
        if "$gte" in value:
            date_value = value["$gte"]
            values.append(
                {"at": {"$lte": (date_value + default_window)}}
            )
        else:
            date_value = value["$lte"]
            values.append(
                {"at": {"gte": (date_value - default_window)}}
            )


def pre_views_get_callback(endpoint: str, pipeline: list):
    times = pipeline[0].get("$match", {}).get("$and", False)
    if times:
        clean_bad_dates(times)
        if endpoint == "stats" and not times:
            pipeline.pop(0)
            return
        set_default_times(times)
    pass


@app.route("/application/config")
def get_config():
    return jsonify(ConfigMap.theme)


app.before_aggregation += pre_views_get_callback

if __name__ == '__main__':
    app.run(host="0.0.0.0")
