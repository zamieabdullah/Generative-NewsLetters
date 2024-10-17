import sys
import os
import json
import re
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

parent_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))

# Add it to the system path
sys.path.append(parent_dir)

if os.getenv('IN_PROD') == "True":
    url = os.getenv('DATABASE_URL')
else:
    url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@" \
                                        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

print(url)
# Create a new SQLAlchemy engine
engine = create_engine(url)

# Create a base class for your models
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Now you can import your module
from models.examples import Titles

def read_jsonl(file_path):
    with open(file_path, 'r', encoding='Windows-1252') as file:
        return [json.loads(line) for line in file]

with open('../example_docs/seo_key_topics.txt', 'r', encoding='Windows-1252') as file:
        seo_terms = [line.strip() for line in file]

session = Session()

try:
    for topic in seo_terms:

        new_title = Titles(titles=topic)
        session.add(new_title)

        # Print the cleaned content
        print(f"Added title: {topic}")

    # Commit all changes after the loop
    session.commit()
    print("All titles added successfully!")

except Exception as e:
    session.rollback()  # Rollback in case of error
    print("Error occurred:", e)

finally:
    session.close()  # Close the session


