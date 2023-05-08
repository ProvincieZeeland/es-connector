# https://tedboy.github.io/flask/index.html

# Import CLI support
from flask import json
from flask.cli import FlaskGroup

# Get the app
from project import app

# create app / cli instance
cli = FlaskGroup(app)

# handle cli requests
if __name__ == "__main__":
    cli()

