"""Evaluator that validates a json string and evaluates it agains a specified schema."""
import json
from jsonschema import validate, ValidationError, SchemaError


class JsonEvaluator:
    def __init__(self, json_schema_path):
        """
        Initialize the evaluator.

        :param json_schema_path: File path to the JSON schema to validate against.
        """
        with open(json_schema_path, "r") as schema_file:
            self.json_schema = json.load(schema_file)

    def load_json(self, json_string):
        """
        Try to load a JSON string into a JSON object.

        :param json_string: The JSON string to load.
        :return: The loaded JSON object if successful, raises a ValueError otherwise.
        """
        try:
            json_object = json.loads(json_string)
            return json_object
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {e}")

    def validate_json(self, json_object, json_schema):
        """
        Validate a JSON object against the specified schema.

        :param json_object: The JSON object to validate.
        :param json_schema: The JSON schema to validate against.
        :return: True if the JSON object is valid, raises a ValidationError otherwise.
        """
        try:
            validate(instance=json_object, schema=json_schema)
            return True
        except ValidationError as e:
            raise ValidationError(f"JSON validation error: {e}")
        except SchemaError as e:
            raise SchemaError(f"Invalid schema: {e}")

    def __call__(self, *, json_string: str, **kwargs):
        """
        Evaluate whether a JSON string can be loaded and validated against the schema.

        :param json_string: The JSON string to evaluate.
        :return: A dictionary with 'valid_json' and 'valid_schema' indicating the validity.
        """

        result = {
            "valid_json": 0,
            "valid_schema": 0
        }

        try:
            json_object = self.load_json(json_string)
            result["valid_json"] = 1
            try:
                self.validate_json(json_object, self.json_schema)
                result["valid_schema"] = 1
            except (ValidationError, SchemaError):
                pass
        except ValueError:
            pass

        return result
    