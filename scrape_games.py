import asyncio
import json
import praw
import re
import time
from discord.ext.commands import Bot

def get_configs(config_file, json_key):
    with open(config_file) as f:
        data = json.load(f)

    return data[json_key]

DISCORD_SECRETS = get_configs("config.json", "discord")
DISCORD_TOKEN = DISCORD_SECRETS["token"]
DISCORD_CHANNEL = DISCORD_SECRETS["channel"]

ACCEPTED_GAME_SITES = re.compile(r"^https:\/\/(www.)?(epicgames|humblebundle|gog|store.steampowered|ubisoft)\.com")

BOT_PREFIX = ("!")
bot = Bot(command_prefix=BOT_PREFIX)

@bot.event
async def on_ready():
    print("Logged in as:")
    print(bot.user.name)
    print(bot.user.id)
    bot.loop.create_task(scrape_gamedealsfree())

async def scrape_gamedealsfree():
    reddit_obj = create_reddit_object()
    gamedealsfree_subreddit = reddit_obj.subreddit("gamedealsfree")

    # I just initialize @date_of_newest_post to a day back so the bot can get yesterday's posts the first time it is run.
    date_of_newest_post = time.time() - (3600*24)

    while True:
        recent_posts = gamedealsfree_subreddit.new(limit=7)  # There usually aren't that many free games a day so I only check the 7 newest posts.
        unread_recent_posts = []
        for post in recent_posts:
            if post.created_utc > date_of_newest_post:
                unread_recent_posts.append(post)

            else:  # Posts are stored from newer to older. Once we reach a post older than date_of_newest post, we've already seen everything else in the list, so we can just break
                break

        if len(unread_recent_posts):
            date_of_newest_post = unread_recent_posts[0].created_utc
            filtered_posts = filter_posts(unread_recent_posts, reddit_obj)
            discord_msg = create_discord_msg(filtered_posts)
            await bot.get_channel(DISCORD_CHANNEL).send(discord_msg)

        # Sleep for two hours
        await asyncio.sleep(3600 * 2)

def create_reddit_object():
    reddit_configs = get_configs("config.json", "reddit")
    reddit = praw.Reddit(client_id=reddit_configs["id"],
                         client_secret=reddit_configs["secret"],
                         user_agent=reddit_configs["agent"],
                         username=reddit_configs["username"],
                         password=reddit_configs["password"])

    return reddit

def filter_posts(unread_posts, reddit_obj):
    filtered_posts = []
    for post in unread_posts:
        linked_submission = reddit_obj.submission(url=post.url)
        if ACCEPTED_GAME_SITES.search(linked_submission.url):
            filtered_posts.append(post.url)

    return filtered_posts

def create_discord_msg(posts):
    discord_msg = ""
    for count, post in enumerate(posts, start=1):
        discord_msg += str(count) + ". " + post + "\n"

    return discord_msg

bot.run(DISCORD_TOKEN)
