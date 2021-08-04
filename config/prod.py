import os
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL").replace("postgres://", "postgresql://")
SQLALCHEMY_TRACK_MODIFICATIONS = True