from instaloader import Instaloader, Profile
from os import listdir, unlink
from os.path import splitext
# Get instance
Archiver = Instaloader()

profile_name = "ttt_official"

profile = Profile.from_username(Archiver.context, profile_name0)

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