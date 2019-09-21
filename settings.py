import os
from datetime import datetime, timedelta

_host = os.getenv("mongo_host", "localhost")
_host_port = int(os.getenv("mongo_port", "27017"))
_host_username = os.getenv("mongo_user", "")
_host_password = os.getenv("mongo_pass", "")
_host_dbname = 'nebula'

_host_login_str = f"{_host_username}:{_host_password}@" if _host_username or _host_password else ""
MONGO_URI = f"mongodb://{_host_login_str}{_host}:{_host_port}"
print(MONGO_URI)

RESOURCE_METHODS = ['GET']
view_collection_name = "views"
book_collection_name = "books"

PAGINATION = False

# MongoDB Query to get the most recent 30mins of data.
# db.views.find({at: {$gt: (new Date(ISODate().getTime() - 1000*60*30))  }},{at:1, _id:0})

joint = {
    ma
}

DOMAIN = {
    'joint': joint,
    'views': {},
    'books': {},
}

