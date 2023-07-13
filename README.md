# scrape-rgamedealsfree

## About

A script that uses Reddit's API (PRAW) to look at reddit.com/r/gamedealsfree and sends a message to Discord via a webhook url.

Each post in the subreddit <https://www.reddit.com/r/gamedealsfree> links to a post from <https://www.reddit.com/r/gamedeals>. Although the script checks the r/gamedealsfree subreddit, it sends links to r/gamedeals posts. The reason I chose to do this is because the r/gamedeals subreddit is much more popular than r/gamedealsfree, so there are usually more comments that give reviews about the game posted. This is also why I chose not to link directly to the gamesite page where the game can be redeemed.

## Built with

- [PRAW: The Python Reddit API Wrapper](https://praw.readthedocs.io/en/latest/)
