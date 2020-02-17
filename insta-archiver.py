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
    short_code = CharField(primary_key=True)
    user = ForeignKeyField(User, backref='posts')
    caption = TextField()
    post_url = CharField()
    created_date = DateTimeField(default=datetime.datetime.now)

db.connect()
db.create_tables([User, Post])

# Get instance
Archiver = Instaloader()

profile_name = "ttt_official"
profile_url = "https://instagram.com/" + profile_name
dbUser, created = User.get_or_create(
    username=profile_name,
    profile_url=profile_url)

profile = Profile.from_username(Archiver.context, dbUser.username)

for instaPost in profile.get_posts():
    # Check if we have already archived this post
    dbPost = Post.get_or_none(Post.short_code == instaPost.shortcode)
    if dbPost is not None:
        print("I have saved this post! I am going! Bye!")
        break
        
    postCaption = ""
    downloaded = Archiver.download_post(instaPost, target=profile_name)
    for f in listdir(profile_name):
        file_path = profile_name + '/' + f
        file_extension = splitext(f)[1]        
        if file_extension == ".txt":
            with open(file_path) as yoF:
                lines = yoF.read()
                postCaption = lines
        elif file_extension == ".json" or file_extension == ".xz":
            unlink(file_path)
            continue
        else:
            print("Found media: " + f)
        unlink(file_path)

    dbPost = Post.create(
        short_code=instaPost.shortcode,
        user=dbUser,
        caption=postCaption,
        post_url="https://instagram.com/p/" + instaPost.shortcode,
        created_date=instaPost.date_utc
    )
    print("Post saved?")
print("And done!")
    