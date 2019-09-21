from eve import Eve
from flask_cors import CORS

from utils.ConfigMap import ConfigMap, add_discovery_path

add_discovery_path("./eve.config.yaml")
app = Eve(settings=ConfigMap.get_singleton().eve.dict)
CORS(app)

if __name__ == '__main__':
    app.run(host="0.0.0.0")
