"""hellobaton tap class."""
from typing import List
from singer_sdk import Tap, Stream
from singer_sdk import typing as th
from tap_hellobaton.streams import (
    ProjectAttachementsStream,
    ProjectUsersStream,
    ProjectsStream,
    CompaniesStream,
    MilestonesStream,
    PhasesStream,
    TasksStream,
    TimeEntriesStream,
    UsersStream,
    TaskAttachmentsStream,
    TemplatesStream,
    ActivityStream,
    CommentsStream,
    CustomFieldsStream,
    CustomFieldValuesStream,
    CustomFieldOptionsStream,
    ExternalTasks,
    MilestoneFeedback,
    TaskDeliverables,
    ProjectPhases,
)

STREAM_TYPES = [
    ProjectsStream,
    CompaniesStream,
    MilestonesStream,
    PhasesStream,
    ProjectUsersStream,
    ProjectAttachementsStream,
    TasksStream,
    TimeEntriesStream,
    UsersStream,
    TaskAttachmentsStream,
    TemplatesStream,
    ActivityStream,
    CommentsStream,
    CustomFieldsStream,
    CustomFieldValuesStream,
    CustomFieldOptionsStream,
    ExternalTasks,
    MilestoneFeedback,
    TaskDeliverables,
    ProjectPhases,
]


class Taphellobaton(Tap):
    """hellobaton tap class."""

    name = "tap-hellobaton"
    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            description="The token to authenticate against the API service",
        ),
        th.Property(
            "company",
            th.StringType,
            required=True,
            description="Company instance to add to the base url",
        ),
        th.Property(
            "user_agent", th.StringType, required=False, description="User agent string"
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
