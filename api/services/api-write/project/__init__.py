##############################################################################
#  
#  ES-Connector API
#
#  API for updating Elasticsearch
#
#  @author Wim Kosten <w.kosten@zeeland.nl>
#
##############################################################################

# Import Flask / template renderer
from flask import Flask
from flask import render_template

import os
import sys

# Add shared modules path
data_path = os.path.join(os.path.dirname(__file__), '../../../', 'shared/models')
sys.path.append(data_path)

# Get blueprints
from .blueprints.general import bp_general
from .blueprints.elasticsearch import bp_elastic

# Create Flask app
app = Flask(__name__)

# If no param / action specified show index.html
@app.route('/')
def index():
    return render_template("index.html")

# Register blueprints with our app
app.register_blueprint(bp_general)
app.register_blueprint(bp_elastic)

