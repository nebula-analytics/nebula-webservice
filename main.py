from eve import Eve
from flask_cors import CORS

app = Eve()
CORS(app)

if __name__ == '__main__':
    app.run(host="0.0.0.0")
