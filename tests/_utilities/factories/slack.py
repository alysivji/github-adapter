import factory

from busy_beaver.models import SlackInstallation as slack_installation_model
from busy_beaver.models import SlackUser as slack_user_model


def SlackInstallation(session):
    class _SlackInstallationFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = slack_installation_model
            sqlalchemy_session_persistence = "commit"
            sqlalchemy_session = session

        authorizing_user_id = "abc"

        bot_access_token = factory.Faker("uuid4")
        bot_user_id = "def"

        scope = "identity chat:message:write"
        workspace_id = "SC234sdfsde"
        workspace_name = "ChiPy"

        organization_name = "Chicago Python"
        workspace_logo_url = (
            "https://www.chipy.org/static/img/chipmunk.1927e65c68a7.png"
        )

    return _SlackInstallationFactory


def SlackUser(session):
    class _SlackUserFactory(factory.alchemy.SQLAlchemyModelFactory):
        class Meta:
            model = slack_user_model
            sqlalchemy_session_persistence = "commit"
            sqlalchemy_session = session

        installation = factory.SubFactory(SlackInstallation(session))
        slack_id = "user_id"

    return _SlackUserFactory
