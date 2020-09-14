import asyncio
import json
import os
import praw
import re
import time
from discord.ext.commands import Bot
#from dotenv import load_dotenv

#load_dotenv()
#DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

BOT_PREFIX = ("!")
bot = Bot(command_prefix=BOT_PREFIX)

@bot.event
async def on_ready():
    print("Logged in as:")
    print(bot.user.name)
    print(bot.user.id)
    bot.loop.create_task(scrape_gamedealsfree())

def get_configs(config_file, json_key):
    with open(config_file) as f:
        data = json.load(f)

    return data[json_key]

def create_reddit_object():
    reddit_configs = get_configs("config.json", "reddit")
    reddit = praw.Reddit(client_id=reddit_configs["id"],
                         client_secret=reddit_configs["secret"],
                         user_agent=reddit_configs["agent"],
                         username=reddit_configs["username"],
                         password=reddit_configs["password"])

    return reddit

async def scrape_gamedealsfree():
    reddit_obj = create_reddit_object()
    gamedealsfree_subreddit = reddit_obj.subreddit("gamedealsfree")

    x = 5
    date_of_newest_post = time.time() - (24*60*60) * x  # for testing, just set it to x days back so we can initially grab all posts from the previous 3 days. probably going to have x = 1 in final version
    print("Date of newest post: ", date_of_newest_post)

    while True:
        recent_posts = gamedealsfree_subreddit.new(limit=7)  # Get the 7 newest posts from r/gamedealsfree. There usually aren't that many free games a day so I only check the 7 newest posts.
        unread_recent_posts = []
        for post in recent_posts:
            if post.created_utc > date_of_newest_post:
                unread_recent_posts.append(post)

            else:  # Posts are stored from newer to older. Once we reach a post older than date_of_newest post, we've already seen everything else in the list, so we can just break
                break

        if len(unread_recent_posts):
            print(unread_recent_posts[0].created_utc)
            date_of_newest_post = unread_recent_posts[0].created_utc
            filtered_posts = filter_posts(unread_recent_posts, reddit_obj)
            discord_msg = create_discord_msg(filtered_posts)
            print(discord_msg)
            await bot.get_channel(DISCORD_CHANNEL).send(discord_msg)

        print("going to sleep for an hour")
        await asyncio.sleep(3600)
        print("woke up")

def filter_posts(unread_posts, reddit_obj):
    accepted_sites_regex = re.compile(r"^https:\/\/(www.)?(epicgames|humblebundle|gog|store.steampowered|ubisoft)\.com")
    filtered_posts = []
    for post in unread_posts:
        linked_submission = reddit_obj.submission(url=post.url)
        if accepted_sites_regex.search(linked_submission.url):
            filtered_posts.append(post.url)
            #print(post.url)

    return filtered_posts

def create_discord_msg(posts):
    discord_msg = ""
    num = 1
    for post in posts:
        discord_msg += str(num) + ". " + post + "\n"
        num += 1

    return discord_msg


def get_discord_token(discord_configs):
    return discord_configs["token"]

DISCORD_TOKEN = get_discord_token(get_configs("config.json", "discord"))
DISCORD_CHANNEL = get_configs("config.json", "discord")["channel"]
bot.run(DISCORD_TOKEN)
