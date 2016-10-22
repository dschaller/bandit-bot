import json
import logging

log = logging.getLogger(__name__)


def post_message(slack_client, channel, text):
    """Post a message."""
    response = slack_client.api_call(
        'chat.postMessage',
        channel=channel,
        text=text,
        as_user=True
    )
    _check_response(response)
    return response


def add_reaction(slack_client, reaction, channel, timestamp):
    """Add a reaction to a message."""
    response = slack_client.api_call(
        'reactions.add',
        name=reaction,
        channel=channel,
        timestamp=timestamp
    )
    _check_response(response)
    return response


def remove_reaction(slack_client, reaction, channel, timestamp):
    """Remove a reaction from a message."""
    response = slack_client.api_call(
        'reactions.remove',
        name=reaction,
        channel=channel,
        timestamp=timestamp
    )
    _check_response(response)
    return response


def get_channel_info(channel, slack_client):
    """Get information about a channel.

    Reference documentation: https://api.slack.com/methods/channels.info.

    Parameters:
        channel: The channel ID.
        slack_client: A slack client.

    Returns:
        A dictionary representing Slack channel information.
    """
    room_info_command = ''
    room = ''
    if channel[0] == 'C':  # Check public channels
        room_info_command = 'channels.info'
        room_key = 'channel'
    else:  # Check group channels
        room_info_command = 'groups.info'
        room_key = 'group'
    response = slack_client.api_call(room_info_command, channel=channel)
    _check_response(response)
    return response.get(room_key)


def get_team_info(slack_client):
    """Get information about a team.

    Reference documentation: https://api.slack.com/methods/team.info.

    Arguments:
        slack_client: A slack client.

    Returns:
        A dictionary representing Slack team information.
    """
    response = slack_client.api_call('team.info')
    _check_response(response)
    return response.get('team')


def _check_response(response):
    try:
        ok_status = response.get('ok')
    except ValueError:
        raise
    if ok_status is None:
        raise RuntimeError(
            'Did not receive ok in Slack API response: {}'.format(response)
        )
    if ok_status is not True:
        raise RuntimeError('Received non-ok Slack API response: {}'.format(response))
