"""
Serialization for supporting idempotency
"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseIdempotencySerializer(ABC):
    """
    Abstract Base Class for Idempotency serialization layer, supporting dict operations.
    """

    @abstractmethod
    def to_dict(self, data: Any) -> Dict:
        pass

    @abstractmethod
    def from_dict(self, data: Dict) -> Any:
        pass


class BaseIdempotencyModelSerializer(BaseIdempotencySerializer):
    """
    Abstract Base Class for Idempotency serialization layer, for using a model as data object representation.
    """

    @classmethod
    @abstractmethod
    def instantiate(cls, model_type: Any) -> BaseIdempotencySerializer:
        """
        Instantiate the serializer from the given model type.
        In case there is the model_type is unknown, None will be sent to the method.
        It's on the implementer to verify that:
        - None is handled
        - A model type not matching the expected types is handled

        Parameters
        ----------
        model_type: Any
            The model type to instantiate the class for

        Returns
        -------
        BaseIdempotencySerializer
            Instance of the serializer class
        """
        pass
