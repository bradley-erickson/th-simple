import random

loading_messages = [
    "Fetching the requested data... Please hold on!",
    "Running analysis, this might take a moment. Your patience is appreciated!",
    "Gathering insights... Thank you for your patience!",
    "Crunching numbers and analyzing data. Hang tight!",
    "We're working hard to get you the information. Please stay with us!",
    "Loading your personalized insights. Just a bit longer!",
    "Thank you for waiting. We're making sure everything is perfect!",
]

def random_message():
    return random.choice(loading_messages)
