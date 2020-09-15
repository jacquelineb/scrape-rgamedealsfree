# scrape-rgamedealsfree

## About

A bot for Discord that uses Reddit's API (PRAW) to look at reddit.com/r/gamedealsfree and sends a message about new posts.

Each post in the subreddit <https://www.reddit.com/r/gamedealsfree> links to a post from <https://www.reddit.com/r/gamedeals>. Although the bot checks the r/gamedealsfree subreddit, it messages links to r/gamedeals. The reason I chose to do this is because the r/gamedeals subreddit is much more popular than r/gamedealsfree, so there are usually more comments that give reviews about the game posted. This is also why I chose not to link directly to the gamesite page where the game can be redeemed.

## Built with
* [Discord API](https://discordpy.readthedocs.io/en/latest/)
* [PRAW: The Python Reddit Api Wrapper](https://praw.readthedocs.io/en/latest/)
