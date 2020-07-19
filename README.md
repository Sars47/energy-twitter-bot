# Hourly Energy Twitter Bot
The code repository for this [energy twitter bot](https://twitter.com/BotHourly). The bot exists to help illustrate that sustainable energy production in the United States is a complex and ever-present problem.

# Context
This script runs at the 5 minute mark every hour according to a chron job scheduled on a raspberry pi. For testing purposes, I recommend printing out generated tweet strings rather than tweeting them to any particular account. You can do this by chaning which line is commented out / uncommented out in the app.py script in the update_status() function.

# Built using
* [US Energy Information Administration's API](https://www.eia.gov/opendata/)
* [Tweepy](https://www.tweepy.org/)

# Got an idea for improvement?
Contact the maintainers or open an issue/pull request.