"""
Templating out python objects so ast can be generated
"""

STREAM_TEMPLATE = """
class {stream_object_name}(hellobatonStream):
    \"""Define custom stream.\"""
    name = "{stream_name}"
    path = "/{stream_name}/"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "{stream_name}.json"
"""