from flask_login import UserMixin
from sqlalchemy_utils import EncryptedType, URLType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from busy_beaver.common.models import BaseModel
from busy_beaver.config import SECRET_KEY
from busy_beaver.extensions import db, login_manager


class SlackInstallation(BaseModel):
    """Keep track of each installation of Slack integration"""

    __tablename__ = "slack_installation"

    def __repr__(self):  # pragma: no cover
        return f"<SlackInstallation: {self.workspace_name}>"

    # Attributes
    authorizing_user_id = db.Column(db.String(300), nullable=False)
    bot_access_token = db.Column(
        EncryptedType(db.String, SECRET_KEY, AesEngine, "pkcs5"), nullable=False
    )
    bot_user_id = db.Column(
        EncryptedType(db.String, SECRET_KEY, AesEngine, "pkcs5"), nullable=False
    )
    scope = db.Column(db.String(800), nullable=False)
    workspace_id = db.Column(db.String(20), index=True, nullable=False)
    workspace_name = db.Column(db.String(255), nullable=False)

    auth_response = db.Column("auth_response", db.JSON)

    # user entered information
    # TODO spin this into a different table
    organization_name = db.Column(db.String(255), nullable=True)
    workspace_logo_url = db.Column(URLType, nullable=True)

    # Relationships
    slack_users = db.relationship(
        "SlackUser", back_populates="installation", lazy="select", cascade="all, delete"
    )
    github_summary_config = db.relationship(
        "GitHubSummaryConfiguration",
        back_populates="slack_installation",
        uselist=False,
        lazy="joined",
        cascade="all, delete",
    )
    upcoming_events_config = db.relationship(
        "UpcomingEventsConfiguration",
        back_populates="slack_installation",
        uselist=False,
        lazy="joined",
        cascade="all, delete",
    )
    cfp_config = db.relationship(
        "CallForProposalsConfiguration",
        back_populates="slack_installation",
        uselist=False,
        lazy="joined",
        cascade="all, delete",
    )


class SlackUser(UserMixin, BaseModel):
    """Track users that have interacted with Busy Beaver on Slack"""

    __tablename__ = "slack_user"

    installation_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "slack_installation.id", name="fk_installation_id", ondelete="CASCADE"
        ),
        index=True,
        nullable=False,
    )
    slack_id = db.Column(db.String(30), index=True, nullable=False)
    app_home_opened_count = db.Column(db.Integer, nullable=False, default=0)

    # Relationships
    installation = db.relationship("SlackInstallation")


@login_manager.user_loader
def load_user(id):
    return SlackUser.query.get(int(id))
