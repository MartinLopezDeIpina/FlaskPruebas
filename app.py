from flask import Flask, render_template, request, redirect, url_for, session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from routes import init_routes

from config import Config
from database import db
from models import Persona

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

migrate = Migrate(app, db)
migrate.init_app(app, db)

init_routes(app)

if __name__ == '__main__':
    app.run()
