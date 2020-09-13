import json
import praw
import re
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
    x = 4
    date_of_newest_post = time.time() - (24*60*60) * x # for testing, just set it to x days back so we can initially grab all posts from the previous 3 days. probably going to have x = 1 in final version
    print("Date of newest post: ", date_of_newest_post)

    reddit = create_reddit_object()
    gamedealsfree_subreddit = reddit.subreddit("gamedealsfree")

    ACCEPTED_SITES_REGEX = re.compile(r"https:\/\/(www.)?(epicgames|humblebundle|gog|store.steampowered)\.com.*")
    while True:
        recent_posts = gamedealsfree_subreddit.new(limit=10)    # Get the 10 newest posts from r/gamedealsfree. There usually aren't that many free games a day so I only check the 10 newest posts
        unread_recent_posts = []
        for post in recent_posts:
            if post.created_utc > date_of_newest_post:
                print("New post found")
                print(post.title, post.created_utc)

                linked_submission = reddit.submission(url=post.url)
                print("LINKED SUBMISSION: " + linked_submission.title)
                print("LINKED SUBMISSION URL: " + linked_submission.url)

                if ACCEPTED_SITES_REGEX.search(linked_submission.url):
                    print("ACCEPTED SITE")
                    unread_recent_posts.append(post)    # Get a list of which posts you haven't seen yet


            else:   # Posts are stored from newer to older. Once we reach a post older than date_of_newest post, we've already seen everything else in the list, so we can just break
                break


        if len(unread_recent_posts):
            date_of_newest_post = unread_recent_posts[0].created_utc

            print_new_posts(unread_recent_posts)


        print("going to sleep for an hour")
        time.sleep(3600)
        print("woke up")

def print_new_posts(unread_posts):
    for post in unread_posts:
        print(post.title, post.created_utc)

def main():
    print("Scraping r/gamedealsfree")
    scrape_gamedealsfree()

main()
