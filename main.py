import datetime
import json
import string
import random
from pprint import pprint
from dotenv import load_dotenv
from sys import exit
from os import listdir, unlink, environ, makedirs, path
from os.path import splitext
from peewee import *
from instaloader import Instaloader, Profile
from shutil import copy2

load_dotenv()

def random_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

# Load runtime variables
DB_CONN_STRING = environ.get("DB_PATH")
if not DB_CONN_STRING:
    exit("Error: Database not found")

USERS_LIST_PATH = environ.get("USERS_LIST_PATH")
if not USERS_LIST_PATH:
    exit("No users provided! Exiting!")

MEDIA_ARCHIVAL_DIRECTORY = environ.get("MEDIA_ARCHIVAL_DIRECTORY")
if not MEDIA_ARCHIVAL_DIRECTORY:
    exit("Please provide path to save media!")

# Initiate DB
DB_CONN_STRING = DB_CONN_STRING + "/app.db"
db = SqliteDatabase(DB_CONN_STRING)
Archiver = Instaloader(
    download_video_thumbnails = False,
    download_comments = False,
    save_metadata = False
)

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
    likes = IntegerField()
    comments = IntegerField()

class PostMedia(BaseModel):
    media_id = CharField(primary_key=True)
    post = ForeignKeyField(Post, backref='media')
    media_type = CharField(constraints=[Check("media_type in ('photo', 'video')")])
    file_name = CharField()
    file_path = CharField()

db.connect()
db.create_tables([User, Post, PostMedia])

def archive_user (profile_name):
    downloadFolderName = "download_data"
    profile_url = "https://instagram.com/" + profile_name
    dbUser, created = User.get_or_create(
        username=profile_name,
        profile_url=profile_url)

    profile = Profile.from_username(Archiver.context, dbUser.username)

    # create directory where all media will be stored
    mediaDirectory = MEDIA_ARCHIVAL_DIRECTORY + '/' + profile_name
    if not path.exists(mediaDirectory):
        makedirs(mediaDirectory)

    for instaPost in profile.get_posts():
        # Check if we have already archived this post
        dbPost = Post.get_or_none(Post.short_code == instaPost.shortcode)
        if dbPost is not None:
            print("I have saved this post! I am going! Bye!")
            break
            
        postCaption = ""
        lstPostMedia = list()
        Archiver.download_post(instaPost, target=downloadFolderName)
        for f in listdir(downloadFolderName):
            file_path = downloadFolderName + '/' + f
            file_extension = splitext(f)[1]
            if file_extension == ".txt":
                with open(file_path) as yoF:
                    lines = yoF.read()
                    postCaption = lines
                unlink(file_path)
            elif file_extension == ".json" or file_extension == ".xz":
                unlink(file_path)
            else:
                lstPostMedia.append(file_path)
            
        dbPost = Post.create(
            short_code=instaPost.shortcode,
            user=dbUser,
            caption=postCaption,
            post_url="https://instagram.com/p/" + instaPost.shortcode,
            created_date=instaPost.date_utc,
            likes=instaPost.likes,
            comments=instaPost.comments
        )

        for postMedia in lstPostMedia:
            file_extension = splitext(postMedia)[1]
            media_id = dbPost.short_code + '_' + random_generator()
            newFileName = media_id + file_extension
            newFilePath = mediaDirectory + '/' + newFileName
            # Copy media to archive folder
            copy2(postMedia, newFilePath)
            media_type = 'video' if file_extension == '.mp4' else 'photo'
            # Save details in DB
            PostMedia.create(
                media_id=media_id,
                post=dbPost,
                media_type=media_type,
                file_name=newFileName,
                file_path=newFilePath
            )
            unlink(postMedia)
        

# Load users to be archived
usersToArchive = []
with open(USERS_LIST_PATH) as fileUsers:
    usersToArchive = json.load(fileUsers)

# Loop over all users found in list
for userName in usersToArchive:
    archive_user(userName)
