from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
