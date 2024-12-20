from typing import Any, Optional, Union, get_args, get_origin

try:
    from types import UnionType
except ImportError:
    UnionType = None

from aws_lambda_powertools.utilities.idempotency.exceptions import (
    IdempotencyModelTypeError,
)


def get_actual_type(model_type: Any) -> Any:
    """
    Extract the actual type from a potentially Optional or Union type.
    This function handles types that may be wrapped in Optional or Union,
    including the Python 3.10+ Union syntax (Type | None).
    Parameters
    ----------
    model_type: Any
        The type to analyze. Can be a simple type, Optional[Type], BaseModel, dataclass
    Returns
    -------
    The actual type without Optional or Union wrappers.
    Raises:
        IdempotencyModelTypeError: If the type specification is invalid
                                   (e.g., Union with multiple non-None types).
    """
    # Check if the type is Optional, Union, or the new Union syntax
    if get_origin(model_type) in (Optional, Union) or (UnionType is not None and get_origin(model_type) is UnionType):
        # Get the arguments of the type (e.g., for Optional[int], this would be (int, NoneType))
        args = get_args(model_type)

        # Filter out NoneType to get the actual type(s)
        actual_type = [arg for arg in args if arg is not type(None)]

        # Ensure there's exactly one non-None type
        if len(actual_type) != 1:
            raise IdempotencyModelTypeError(
                "Invalid type: expected a single type, optionally wrapped in Optional or Union with None.",
            )
        return actual_type[0]

    return model_type
