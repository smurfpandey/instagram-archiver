import datetime
from peewee import *
from dotenv import load_dotenv
from sys import exit
from instaloader import Instaloader, Profile
from os import listdir, unlink, environ
from os.path import splitext

load_dotenv()

# Initiate DB
DB_CONN_STRING = environ.get("DB_PATH")
if not DB_CONN_STRING:
    exit("Error: Database not found")

DB_CONN_STRING = DB_CONN_STRING + "/app.db"
db = SqliteDatabase(DB_CONN_STRING)

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    username = CharField(primary_key=True)
    profile_url = CharField()

class Post(BaseModel):
    user = ForeignKeyField(User, backref='tweets')
    caption = TextField()
    created_date = DateTimeField(default=datetime.datetime.now)

class PostMedia(BaseModel):
    user = ForeignKeyField(User, backref='tweets')
    message = TextField()
    created_date = DateTimeField(default=datetime.datetime.now)
    is_published = BooleanField(default=True)

db.connect()
db.create_tables([User, Post, PostMedia])

# Get instance
Archiver = Instaloader()

profile_name = "ttt_official"

profile = Profile.from_username(Archiver.context, profile_name)

for post in profile.get_posts():
    print("Got post: https://instagram.com/p/" + post.shortcode)

    # Check if we have already archived this post
    # If yes: break
    # If no: proceed

    downloaded = Archiver.download_post(post, target=profile_name)
    if not downloaded:
        break

print("And done!")
    # 
    # for f in listdir(profile_name):
    #     file_path = profile_name + '/' + f
    #     file_extension = splitext(f)[1]        
    #     if file_extension == ".txt":
    #         with open(file_path) as yoF:
    #             lines = yoF.read()
    #             #print("Caption: " + lines)
    #     elif file_extension == ".json" or file_extension == ".xz":
    #         unlink(file_path)
    #         continue
    #     else:
    #         print("Found media: " + f)
    #     unlink(file_path)