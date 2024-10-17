from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from models.model import db
import os

# importing environment variables 
from dotenv import load_dotenv
load_dotenv()

# importing models
from models.blogposts import BlogPosts
from models.examples import Examples, Keywords, Titles

# importing routes
from views.blogposts import bp as blogpost_routes

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# Configure PostgreSQL connection
print(os.getenv('IN_PROD'), flush=True)
if os.getenv('IN_PROD') == "True":
    url = os.getenv('DATABASE_URL')
else:
    url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@" \
                                        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

app.config['SQLALCHEMY_DATABASE_URI'] = url

db.init_app(app)
migrate = Migrate(app, db)
app.config['SQLALCHEMY_ECHO'] = True

# Create the database tables (if they don't exist)
with app.app_context():

    db.create_all()


# Register the routes blueprint
app.register_blueprint(blogpost_routes)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

if __name__ == '__main__':
    app.run()
