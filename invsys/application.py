from flask import Flask, jsonify
from database import db
from blueprints.continuous_resource_blueprint import create_continuous_resource_blueprint
import os
import logging

logger = logging.getLogger(__name__)

def create_app(db_uri: str) -> Flask:
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Register continuous resource blueprints
    app.register_blueprint(
        create_continuous_resource_blueprint(
            blueprint_name="CarsBlueprint",
            resource_type="Car",
            resource_prefix="cars"
        ),
        url_prefix='/api'
    )

    app.register_blueprint(
        create_continuous_resource_blueprint(
            blueprint_name="LorrysBlueprint",
            resource_type="Lorry",
            resource_prefix="lorries"
        ),
        url_prefix='/api'
    )

    app.register_blueprint(
        create_continuous_resource_blueprint(
            blueprint_name="TrucksBlueprint",
            resource_type="Truck",
            resource_prefix="trucks"
        ),
        url_prefix='/api'
    )

    return app


if __name__=="__main__":
    app = create_app(db_uri="sqlite3://red.db")
    app.run("127.0.0.1", 5000)
