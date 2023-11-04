from django.core.exceptions import ValidationError


def validate_votes(value):
    """
    The function `validate_votes` checks if a given value is a positive number
    and raises a `ValidationError` if it is not.

    :param value: The parameter "value" represents the number of votes
    """
    if value < 0:
        raise ValidationError(
            "Votes' value is not an positive number"
        )


def validate_text(value):
    """
    The function `validate_text` checks if a text value is empty and raises a `ValidationError` if it is.

    :param value: The `value` parameter is the text value that needs to be validated
    """
    if value == "":
        raise ValidationError(
            "Text value cannot be empty"
        )


def validate_userid(value):
    """
    The function `validate_userid` checks if an userid length is invalid and raises a `ValidationError` if it is.

    :param value: The `value` parameter is the userid value that needs to be validated
    """
    if len(value) != 20:
        raise ValidationError(
            "Userid has improper length."
        )
