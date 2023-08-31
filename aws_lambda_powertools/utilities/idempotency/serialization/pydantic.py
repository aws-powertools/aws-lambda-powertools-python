from typing import Any, Dict, Type

from pydantic import BaseModel

from aws_lambda_powertools.utilities.idempotency.exceptions import (
    IdempotencyModelTypeError,
    IdempotencyNoSerializationModelError,
)
from aws_lambda_powertools.utilities.idempotency.serialization.base import (
    BaseIdempotencyModelSerializer,
    BaseIdempotencySerializer,
)

Model = BaseModel


class PydanticSerializer(BaseIdempotencyModelSerializer):
    def __init__(self, model: Type[Model]):
        """
        Parameters
        ----------
        model: Model
            A Pydantic model of the type to transform
        """
        self.__model: Type[Model] = model

    def to_dict(self, data: Model) -> Dict:
        if callable(getattr(data, "model_dump", None)):
            # Support for pydantic V2
            return data.model_dump()  # type: ignore[unused-ignore,attr-defined]
        return data.dict()

    def from_dict(self, data: Dict) -> Model:
        if callable(getattr(self.__model, "model_validate", None)):
            # Support for pydantic V2
            return self.__model.model_validate(data)  # type: ignore[unused-ignore,attr-defined]
        return self.__model.parse_obj(data)

    @classmethod
    def instantiate(cls, model_type: Any) -> BaseIdempotencySerializer:
        if model_type is None:
            raise IdempotencyNoSerializationModelError("No serialization model was supplied")

        if not issubclass(model_type, BaseModel):
            raise IdempotencyModelTypeError("Model type is not inherited from pydantic BaseModel")

        return cls(model=model_type)
