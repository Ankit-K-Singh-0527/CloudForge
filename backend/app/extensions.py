
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Database extension, initialized by the application factory.
db = SQLAlchemy()

# Database migration extension.
migrate = Migrate()
