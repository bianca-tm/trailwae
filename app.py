from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

OVERPASS_URL = "http://overpass-api.de/api/interpreter"

@app.route('/trails', methods=['GET'])
def get_trails():
    latitude = request.args.get('lat')
    longitude = request.args.get('lon')
    radius = request.args.get('radius', 10)  # Default radius in km

    if not latitude or not longitude:
        return jsonify({'error': 'Latitude and Longitude are required parameters.'}), 400

    query = f"""
    [out:json];
    (
      way(around:{radius * 1000},{latitude},{longitude})["highway"="path"];
      way(around:{radius * 1000},{latitude},{longitude})["highway"="footway"];
      way(around:{radius * 1000},{latitude},{longitude})["highway"="track"];
    );
    out body;
    >;
    out skel qt;
    """

    response = requests.get(OVERPASS_URL, params={'data': query})

    if response.status_code == 200:
        data = response.json()
        trails = []
        for element in data['elements']:
            if element['type'] == 'way':
                trail = {
                    'id': element['id'],
                    'nodes': element['nodes'],
                    'tags': element.get('tags', {})
                }
                trails.append(trail)
        return jsonify(trails)
    else:
        return jsonify({'error': 'Failed to fetch trails data'}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
