import asyncio
import praw
import re
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
REDDIT = praw.Reddit(
    client_id=os.getenv("REDDIT_ID"),
    client_secret=os.getenv("REDDIT_SECRET"),
    user_agent=os.getenv("REDDIT_AGENT"),
)

ACCEPTED_GAME_SITES = re.compile(
    r"^https:\/\/(www.)?(store.epicgames|humblebundle|gog|store.steampowered|ubisoft)\.com"
)


def get_unread_submissions(recent_submissions, last_read_date):
    unread_submissions = []
    for submission in recent_submissions:
        # Recent_submissions are stored from newer to older.
        # Once we reach a submission older than last_read_date, we've already seen everything else in the list, so we can just break
        if submission.created_utc > last_read_date:
            unread_submissions.append(submission)

        else:
            break

    return unread_submissions


def get_acceptable_submissions(unread_submissions):
    """Return a list of r/gamedeals urls (strings) that reference games redeemed from a certain selection of sites.

    Each Submission in @unread_submissions comes from r/gamedealsfree. An r/gamedealsfree Submission links to an r/gamedeals Submission,
    and an r/gamedeals Submission links to a game site.

    The url of the gamesite linked from the r/gamedeals Submission is checked against a regex (ACCEPTED_GAME_SITES) to
    determine if it comes from the accepted selection of sites. If so, the url of the r/gamedeals Submission
    (NOT the r/gamedealsfree submission) is added to the returned list @acceptable_submissions.
    """

    acceptable_submissions = []
    for submission in unread_submissions:
        linked_submission = REDDIT.submission(url=submission.url)
        if ACCEPTED_GAME_SITES.search(linked_submission.url):
            acceptable_submissions.append(submission.url)

    return acceptable_submissions


def create_discord_msg(submissions):
    discord_msg = f"Found {len(submissions)} free game(s) on r/gamedealsfree\n"
    for count, submission in enumerate(submissions, start=1):
        discord_msg += str(count) + ". " + submission + "\n"

    return discord_msg


async def scrape_gamedealsfree():
    gamedealsfree_subreddit = REDDIT.subreddit("gamedealsfree")

    # I just initialize @date_of_newest_submission to a day back so the bot can get some submissions the first time it is run.
    date_of_newest_submission = time.time() - (3600 * 24)

    while True:
        print("Checking r/gamedealsfree...")
        # There usually aren't that many free games a day so I only check the 10 newest submissions.
        recent_submissions = gamedealsfree_subreddit.new(limit=10)
        unread_submissions = get_unread_submissions(
            recent_submissions, date_of_newest_submission
        )

        if len(unread_submissions):
            date_of_newest_submission = unread_submissions[0].created_utc
            acceptable_submissions = get_acceptable_submissions(unread_submissions)

            if len(acceptable_submissions):
                discord_msg = create_discord_msg(acceptable_submissions)
                result = requests.post(
                    DISCORD_WEBHOOK_URL, json={"content": discord_msg}
                )

                try:
                    result.raise_for_status()
                except requests.exceptions.HTTPError as err:
                    print(err)
                else:
                    print(f"Payload delivered successfully, code {result.status_code}.")

        print("Done. Checking again in 2 hours...")
        await asyncio.sleep(3600 * 2)


asyncio.run(scrape_gamedealsfree())
