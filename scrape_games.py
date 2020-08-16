import json
import praw
import time

def create_reddit_object(json_file = "reddit_config.json", json_key="reddit_creds"):
    with open(json_file) as f:
        data = json.load(f)

    reddit_credentials = data[json_key]
    reddit = praw.Reddit(client_id=reddit_credentials["id"],
                         client_secret=reddit_credentials["secret"],
                         user_agent=reddit_credentials["agent"],
                         username=reddit_credentials["username"],
                         password=reddit_credentials["password"])

    return reddit

def scrape_gamedealsfree():
    x = 3
    date_of_newest_post = time.time() - (24*60*60) * x # for testing, just set it to x days back so we can initially grab all posts from the previous 3 days. probably going to have x = 1 in final version
    print(date_of_newest_post)

    reddit = create_reddit_object()
    r_gamedealsfree = reddit.subreddit("gamedealsfree")

    recent_posts = r_gamedealsfree.new(limit=10)    # Get the 10 newest posts from r/gamedealsfree. There usually aren't that many free games a day so I only check the 10 newest posts
    unread_recent_posts = []
    for post in recent_posts:
        print(post.title, post.created_utc)
        if post.created_utc > date_of_newest_post:
            print("this was a new post")
            unread_recent_posts.append(post)    # Get a list of which posts you haven't seen yet

        else:   # Since the posts are stored from newer to older, once we reach a post older than date_of_newest post, we've already seen everything else in the list, so we can just break
            break

    if len(unread_recent_posts):
        date_of_newest_post = unread_recent_posts[0].created_utc

        for unread_post in unread_recent_posts:
            print(unread_post.created_utc)

scrape_gamedealsfree()