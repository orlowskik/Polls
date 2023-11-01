from django.core.exceptions import ValidationError


def validate_votes(value):
    if value < 0:
        raise ValidationError(
            "Votes' value is not an positive number"
        )


def validate_text(value):
    if value == "":
        raise ValidationError(
            "Text value cannot be empty"
        )