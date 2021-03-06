import logging

from .blocks import AppHome
from .interactors import generate_help_text
from busy_beaver.common.wrappers import SlackClient
from busy_beaver.extensions import db
from busy_beaver.models import SlackInstallation, SlackUser
from busy_beaver.toolbox import EventEmitter

logger = logging.getLogger(__name__)
subscription_dispatch = EventEmitter()
event_dispatch = EventEmitter()


GITHUB_SUMMARY_CHANNEL_JOIN_MESSAGE = (
    "Welcome to <#{channel}>! I'm Busy Beaver. "
    "I post daily summaries of public GitHub activity "
    "in this channel.\n\n"
    "To connect your GitHub account and share activity, "
    "please register using `/busybeaver connect`."
)


def process_event_subscription_callback(data):
    logger.info("Process Event Subscription webhook", extra={"type": data["type"]})
    return subscription_dispatch.emit(data["type"], default="not_found", data=data)


#######################
# Subscription Handlers
#######################
@subscription_dispatch.on("not_found")
@event_dispatch.on("not_found")
def command_not_found(data):
    logger.info("[Busy Beaver] Unknown command")
    return None


@subscription_dispatch.on("url_verification")
def url_verification_handler(data):
    logger.info("[Busy Beaver] Slack -- API Verification")
    return {"challenge": data["challenge"]}


@subscription_dispatch.on("event_callback")
def event_callback_dispatcher(data):
    logger.info(
        f"Process Event Callback -- {data['event']['type']}",
        extra={"event_type": data["event"]["type"]},
    )
    return event_dispatch.emit(data["event"]["type"], default="not_found", data=data)


################
# Event Handlers
################
@event_dispatch.on("message")
def message_handler(data):
    event = data["event"]
    user_id = event["user"]
    if event.get("bot_id") or event.get("subtype") == "bot_message":
        return None

    user_messages_bot = event["channel_type"] == "im"
    if user_messages_bot:
        params = {"workspace_id": data["team_id"]}
        installation = SlackInstallation.query.filter_by(**params).first()

        logger.info("[Busy Beaver] Slack -- Unknown command")
        slack = SlackClient(installation.bot_access_token)
        help_text = generate_help_text(installation, user_id)
        slack.post_message(help_text, channel=data["event"]["channel"])

    return None


@event_dispatch.on("member_joined_channel")
def member_joined_channel_handler(data):
    workspace_id = data["team_id"]
    user_id = data["event"]["user"]
    channel = data["event"]["channel"]

    installation = SlackInstallation.query.filter_by(workspace_id=workspace_id).first()

    # Handle if new user joins channel
    config = installation.github_summary_config
    if not config:
        return None

    user_joins_github_summary_channel = (config.channel == channel) and config.enabled
    if user_joins_github_summary_channel:
        slack = SlackClient(installation.bot_access_token)
        slack.post_ephemeral_message(
            GITHUB_SUMMARY_CHANNEL_JOIN_MESSAGE.format(channel=channel),
            channel=channel,
            user_id=user_id,
        )

    return None


@event_dispatch.on("app_home_opened")
def app_home_handler(data):
    """Display App Home

    Currently we do show first-time viewers a separate screen... should we?
    """
    logger.info("app_home_opened Event", extra=data)
    workspace_id = data["team_id"]
    user_id = data["event"]["user"]
    tab_opened = data["event"]["tab"]

    if tab_opened != "home":
        return None

    installation = SlackInstallation.query.filter_by(workspace_id=workspace_id).first()
    params = {"installation_id": installation.id, "slack_id": user_id}
    user = SlackUser.query.filter_by(**params).first()
    if not user:
        logger.info("First app_home_opened for user", extra=data)
        user = SlackUser(**params)
        user.app_home_opened_count = 0

    user.app_home_opened_count += 1
    db.session.add(user)
    db.session.commit()

    github_summary_channel = None
    github_summary_configured = installation.github_summary_config
    if github_summary_configured:
        github_summary_channel = installation.github_summary_config.channel

    app_home = AppHome(
        github_summary_channel=github_summary_channel,
        upcoming_events_config=installation.upcoming_events_config,
    )

    slack = SlackClient(installation.bot_access_token)
    slack.display_app_home(user_id, view=app_home.to_dict())
    return None


@event_dispatch.on("app_uninstalled")
def app_uninstalled_handler(data):
    workspace_id = data["team_id"]
    installation = SlackInstallation.query.filter_by(workspace_id=workspace_id).first()

    if not installation:
        logger.error("Workspace not found", extra={"workspace_id": workspace_id})
        return {}

    db.session.delete(installation)
    db.session.commit()

    return {}
