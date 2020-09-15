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

BOT_PREFIX = ("!")
bot = Bot(command_prefix=BOT_PREFIX)

ACCEPTED_GAME_SITES = re.compile(r"^https:\/\/(www.)?(epicgames|humblebundle|gog|store.steampowered|ubisoft)\.com")

@bot.event
async def on_ready():
    print("Logged in as:")
    print(bot.user.name)
    print(bot.user.id)
    bot.loop.create_task(scrape_gamedealsfree())

def get_unread_recent_submissions(recent_submissions, date_of_newest_submission):
    unread_submissions = []
    for submission in recent_submissions:
        # Recent_submissions are stored from newer to older.
        # Once we reach a submission older than date_of_newest_submission, we've already seen everything else in the list, so we can just break
        if submission.created_utc > date_of_newest_submission:
            unread_submissions.append(submission)

        else:
            break

    return unread_submissions

async def scrape_gamedealsfree():
    reddit_obj = create_reddit_object()
    gamedealsfree_subreddit = reddit_obj.subreddit("gamedealsfree")

    # I just initialize @date_of_newest_submission to a day back so the bot can get yesterday's submissions the first time it is run.
    date_of_newest_submission = time.time() - (3600*24)

    while True:
        # There usually aren't that many free games a day so I only check the 7 newest submissions.
        recent_submissions = gamedealsfree_subreddit.new(limit=7)
        unread_recent_submissions = get_unread_recent_submissions(recent_submissions, date_of_newest_submission)

        if len(unread_recent_submissions):
            date_of_newest_submission = unread_recent_submissions[0].created_utc
            filtered_submissions = filter_submissions(unread_recent_submissions, reddit_obj)
            discord_msg = create_discord_msg(filtered_submissions)
            await bot.get_channel(DISCORD_CHANNEL).send(discord_msg)

        await asyncio.sleep(3600 * 2)

def create_reddit_object():
    reddit_configs = get_configs("config.json", "reddit")
    reddit = praw.Reddit(client_id=reddit_configs["id"],
                         client_secret=reddit_configs["secret"],
                         user_agent=reddit_configs["agent"],
                         username=reddit_configs["username"],
                         password=reddit_configs["password"])

    return reddit

def filter_submissions(unread_submissions, reddit_obj):
    """Return a list of r/gamedeals urls (strings) that reference games redeemed from a certain selection of sites.

    Each Submission in @unread_submissions comes from r/gamedealsfree. An r/gamedealsfree Submission links to an r/gamedeals Submission,
    and an r/gamedeals Submission links to a game site.

    The url of the gamesite linked from the r/gamedeals Submission is checked against a regex (ACCEPTED_GAME_SITES) to
    determine if it comes from the accepted selection of sites. If so, the url of the r/gamedeals Submission
    (NOT the r/gamedealsfree submission) is added to the returned list @filtered_submissions.
    """

    filtered_submissions = []
    for submission in unread_submissions:
        linked_submission = reddit_obj.submission(url=submission.url)
        if ACCEPTED_GAME_SITES.search(linked_submission.url):
            filtered_submissions.append(submission.url)

    return filtered_submissions

def create_discord_msg(submissions):
    discord_msg = ""
    for count, submission in enumerate(submissions, start=1):
        discord_msg += str(count) + ". " + submission + "\n"

    return discord_msg

bot.run(DISCORD_TOKEN)
