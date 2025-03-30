from flask import Flask
from backend.models import db
import os
from flask_migrate import Migrate

app = None
migrate = None

def setup_app():
    global app
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_app_db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["SECRET_KEY"] = "xyshhfjf"
     

    # Initialize the database with app context
    db.init_app(app)

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    # Create tables only if they don't exist yet
    with app.app_context():
        if not os.path.exists("my_app_db.sqlite3"):
            db.create_all()

    app.app_context().push()

    app.debug = True

setup_app()

# Now import routes after app setup to avoid circular imports
from backend.routes import *

if __name__ == "__main__":
    app.run()
