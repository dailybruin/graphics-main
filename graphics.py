from flask import Flask, render_template
from werkzeug.contrib.cache import SimpleCache
import os
import json
from glob import glob

app = Flask(__name__)
cache = SimpleCache()


# expect GRAPHICS_DIR, an environment variable, to be set with
# the path to the project directory on the graphics server
GRAPHICS_DIR = os.environ.get('GRAPHICS_DIR', '.')


# generate the list of sites, assuming each subfolder has a
# metadata.json with the following format:
# {
#   "title": "Project Title",
#   "description": "Short description"
#   "image": "name_of_image.jpeg"
# }
def generate_sites():
    sites = []
    for directory in glob(GRAPHICS_DIR + '/*/'):
        try:
            with open(directory + 'metadata.json') as data:
                directory =  \
                    '/' + \
                    os.path.basename(os.path.normpath(directory)) + \
                    '/'
                data = json.load(data)
                sites.append(
                    {
                        'path': directory,
                        'title': data['title'],
                        'description': data['description'],
                        'image': directory + data['image'],
                    })
        except Exception as ex:
            app.logger.error(ex)
    return sites


@app.route('/')
def index():
    sites = cache.get('sites')
    if sites is None:
        sites = generate_sites()
        cache.set('sites', sites, timeout=60*60*24)
    return render_template('./index.html', sites=sites)

if __name__ == '__main__':
    app.run(debug=True)
