# BanditBot
A Slack bot that listens for high entropy words in messages.


# Configuration
BanditBot relies on environment variables for it's configuration. The following environment variables can be used for configuration.

| Environment Variable Name | Value Type |
| ------------------------- | ---------- |
| `SLACK_TOKEN` | `String` |


# Running BanditBot
To run BanditBot ensure that the `SLACK_TOKEN` environment variable is set and run `make run`.

BanditBot will tell you when it's connected in it's logs...
```bash
016-10-21 23:53:32,815 INFO:Connecting...
2016-10-21 23:53:32,867 INFO:Starting new HTTPS connection (1): slack.com
2016-10-21 23:53:34,016 INFO:BanditBot is connected...
2016-10-21 23:53:34,120 INFO:BanditBot is online...
```

# Developing BanditBot
To develop BanditBot setup a virtualenv. If you are unfamiliar with how to set one up there is a good walkthrough [here](http://docs.python-guide.org/en/latest/dev/virtualenvs/).
Run the following commands once you're in your virtualenv. This assumes the virtualenv is named banditbot.

```bash
pip install -r requirements.txt
```

# Testing BanditBot
To test BanditBot follow the steps in [Developing BanditBot](#developing-banditbot) and run
```bash
make test
```

---
##### Acknowledgements
* Thanks to [lyft/bandit-high-entropy-string](https://github.com/lyft/bandit-high-entropy-string/) for high entropy word patterns.
