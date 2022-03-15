"""Stream type classes for tap-hellobaton."""

from pathlib import Path
from tap_hellobaton.client import hellobatonStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")

class ProjectsStream(hellobatonStream):
    """Define custom stream."""
    name = "projects"
    path = "/projects/"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "projects.json"

class CompaniesStream(hellobatonStream):
    """Define custom stream."""
    name = "companies"
    path = "/companies/"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "companies.json"

class MilestonesStream(hellobatonStream):
    """Define custom stream."""
    name = "milestones"
    path = "/milestones/"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "milestones.json"

class PhasesStream(hellobatonStream):
    """Define custom stream."""
    name = "phases"
    path = "/phases/"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "phases.json"

class ProjectAttachementsStream(hellobatonStream):
    """Define custom stream."""
    name = "project_attachments"
    path = "/project_attachments/"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "project_attachments.json"

class ProjectUsersStream(hellobatonStream):
    """Define custom stream."""
    name = "project_users"
    path = "/project_users/"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "project_users.json"

class TasksStream(hellobatonStream):
    """Define custom stream."""
    name = "tasks"
    path = "/tasks/"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "tasks.json"

class TaskAttachmentsStream(hellobatonStream):
    """Define custom stream."""
    name = "task_attachments"
    path = "/task_attachments/"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "task_attachments.json"

class TemplatesStream(hellobatonStream):
    """Define custom stream."""
    name = "templates"
    path = "/templates/"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "templates.json"

class TimeEntriesStream(hellobatonStream):
    """Define custom stream."""
    name = "time_entries"
    path = "/time_entries/"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "time_entries.json"

class UsersStream(hellobatonStream):
    """Define custom stream."""
    name = "users"
    path = "/users/"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "users.json"

class ActivityStream(hellobatonStream):
    """Define custom stream."""
    name = "activity"
    path = "/activity/"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "activity.json"

class CommentsStream(hellobatonStream):
    """Define custom stream."""
    name = "comments"
    path = "/comments/"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "comments.json"

class CustomFieldsStream(hellobatonStream):
    """Define custom stream."""
    name = "custom_fields"
    path = "/custom_fields/"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "custom_fields.json"

class CustomFieldOptionsStream(hellobatonStream):
    """Define custom stream."""
    name = "custom_field_options"
    path = "/custom_field_options/"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "custom_field_options.json"

class CustomFieldValuesStream(hellobatonStream):
    """Define custom stream."""
    name = "custom_field_values"
    path = "/custom_field_values/"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "custom_field_values.json"
