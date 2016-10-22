import gevent
import logging
import os
import re
import sys

from slackclient import SlackClient

from clients import slack

log = logging.getLogger(__name__)

ENTROPY_PATTERNS_TO_FLAG = [
    # AWS access keys (which often have secret keys listed with them)
    re.compile('AKIA'),
    # URLs with username/password combos
    re.compile('^[a-z]+://.*:.*@'),
    # PEM encoded PKCS8 private keys
    re.compile('BEGIN.*PRIVATE KEY'),
    # Low secret hints
    re.compile(r'[a-z0-9_\.]+key[a-z0-9_\.]*', re.IGNORECASE),
    re.compile(r'pw', re.IGNORECASE),
    re.compile(r'tok', re.IGNORECASE),
    re.compile(r'tkn', re.IGNORECASE),
    re.compile(r'random', re.IGNORECASE),
    re.compile(r'auth', re.IGNORECASE),
    # High secret hints
    re.compile(r'secret', re.IGNORECASE),
    re.compile(r'pass', re.IGNORECASE),
    re.compile(r'passwd', re.IGNORECASE),
    re.compile(r'password', re.IGNORECASE),
    re.compile(r'login', re.IGNORECASE)
]
SLACK_TOKEN = os.environ.get('SLACK_TOKEN')


class SlackBot(object):
    """Wraps the slack bot."""
    def __init__(self):
        self.slack_client = SlackClient(SLACK_TOKEN)
        self.connect()
        self.read()

    def connect(self):
        log.info('Connecting...')
        self.slack_client.rtm_connect()
        log.info('BanditBot is connected...')

    def read(self):
        while True:
            for event in self.slack_client.rtm_read():
                gevent.spawn(self.process_rtm_event, event)
            gevent.sleep(0.1)

    def process_rtm_event(self, event):
        """Dispatcher for RTM event types."""
        if event.get('type') == 'hello':
            log.info('BanditBot is online...')
            return

        if _message_from_bot(event):
            return

        event_type = event.get('type')
        event_subtype = event.get('subtype')

        if event_subtype == 'message_changed':
            self.process_message_changed_event(event)
        if event_type != 'message':
            # log.warning('Did not recognize event: {0!r}'.format(event))
            return

        try:
            self.process_message_event(event)
        except Exception as e:
            log.exception('Error processing slack RTM event {}: {}'.format(event, e))
        # Interesting use case here would be to flag sensitive fields using emoticons
        # elif (event_type == 'reaction_added' or event_type == 'reaction_removed'):
        #     self.reaction_handler.handle(event)

    def process_message_changed_event(self, event):
        channel = event.get('channel')
        previous_message = event.get('previous_message', {})
        user = previous_message.get('user')
        timestamp = previous_message.get('ts')
        for pattern in ENTROPY_PATTERNS_TO_FLAG:
            if not pattern.search(previous_message.get('text')):
                continue
            new_text = event.get('message', {}).get('text')
            if pattern.search(new_text):
                continue
            slack.remove_reaction(self.slack_client, 'lock', channel, timestamp)
            slack.post_message(self.slack_client, user, 'Password succesfully redacted.')
            return

    def process_message_event(self, event):
        """Process a RTM event."""
        if event.get('subtype', '') == 'message_deleted':
            return
        event_text = event.get('text')
        if not event_text:
            return

        user = event.get('user')
        timestamp = event.get('ts')
        channel = event.get('channel')
        for pattern in ENTROPY_PATTERNS_TO_FLAG:
            if not pattern.search(event.get('text')):
                continue
            original_msg = self._compose_message_link(channel, timestamp)
            slack.post_message(
                self.slack_client,
                user,
                'POSSIBLE PASSWORD IN MESSAGE!\n<{}>'.format(original_msg)
            )
            slack.add_reaction(self.slack_client, 'lock', channel, timestamp)
            return

    def _compose_message_link(self, channel, timestamp):
        domain = slack.get_team_info(self.slack_client).get('domain')
        channel_name = slack.get_channel_info(channel, self.slack_client).get('name')
        timestamp = timestamp.replace('.', '')
        return 'https://{}.slack.com/archives/{}/p{}'.format(
            domain,
            channel_name,
            timestamp
        )


def _message_from_bot(event):
    return event.get('subtype') == 'bot_message' or event.get('bot_id') is not None


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(message)s',
        level=logging.DEBUG
    )
    if not SLACK_TOKEN:
        log.error('Error starting banditbot: SLACK_TOKEN is undefined in environment')
        sys.exit(1)

    SlackBot()
