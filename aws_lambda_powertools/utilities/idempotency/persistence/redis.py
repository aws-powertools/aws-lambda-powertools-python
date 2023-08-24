import datetime
import logging
from typing import Any, Dict, Union

try:
    import redis  # type:ignore
except ImportError:
    redis = None


import redis

from aws_lambda_powertools.utilities.idempotency import BasePersistenceLayer
from aws_lambda_powertools.utilities.idempotency.exceptions import (
    IdempotencyItemAlreadyExistsError,
    IdempotencyItemNotFoundError,
    IdempotencyRedisClientConfigError,
)
from aws_lambda_powertools.utilities.idempotency.persistence.base import (
    STATUS_CONSTANTS,
    DataRecord,
)

logger = logging.getLogger(__name__)


class RedisCachePersistenceLayer(BasePersistenceLayer):
    def __init__(
        self,
        connection: Union[redis.Redis, redis.cluster.RedisCluster],
        in_progress_expiry_attr: str = "in_progress_expiration",
        status_attr: str = "status",
        data_attr: str = "data",
        validation_key_attr: str = "validation",
    ):
        """
        Initialize the Redis Persistence Layer
        Parameters
        ----------
        in_progress_expiry_attr: str, optional
            Redis hash attribute name for in-progress expiry timestamp, by default "in_progress_expiration"
        status_attr: str, optional
            Redis hash attribute name for status, by default "status"
        data_attr: str, optional
            Redis hash attribute name for response data, by default "data"
        validation_key_attr: str, optional
            Redis hash attribute name for hashed representation of the parts of the event used for validation
        """

        # Initialize connection with Redis

        if not hasattr(connection, "get_connection_kwargs"):
            raise IdempotencyRedisClientConfigError
        if not connection.get_connection_kwargs().get("decode_responses", False):
            # Requires decode_responses to be true
            raise IdempotencyRedisClientConfigError
        self._connection = connection

        self.in_progress_expiry_attr = in_progress_expiry_attr
        self.status_attr = status_attr
        self.data_attr = data_attr
        self.validation_key_attr = validation_key_attr
        super(RedisCachePersistenceLayer, self).__init__()

    def _item_to_data_record(self, idempotency_key: str, item: Dict[str, Any]) -> DataRecord:
        in_progress_expiry_timestamp = item.get(self.in_progress_expiry_attr)
        if isinstance(in_progress_expiry_timestamp, str):
            in_progress_expiry_timestamp = int(in_progress_expiry_timestamp)
        return DataRecord(
            idempotency_key=idempotency_key,
            status=item[self.status_attr],
            in_progress_expiry_timestamp=in_progress_expiry_timestamp,
            response_data=str(item.get(self.data_attr)),
            payload_hash=str(item.get(self.validation_key_attr)),
        )

    def _get_record(self, idempotency_key) -> DataRecord:
        # See: https://redis.io/commands/hgetall/
        response = self._connection.hgetall(idempotency_key)

        try:
            item = response
        except KeyError:
            raise IdempotencyItemNotFoundError
        return self._item_to_data_record(idempotency_key, item)

    def _put_record(self, data_record: DataRecord) -> None:
        item: Dict[str, Any] = {}

        # Redis works with hset to support hashing keys with multiple attributes
        # See: https://redis.io/commands/hset/
        item = {
            "name": data_record.idempotency_key,
            "mapping": {
                self.status_attr: data_record.status,
            },
        }

        if data_record.in_progress_expiry_timestamp is not None:
            item["mapping"][self.in_progress_expiry_attr] = data_record.in_progress_expiry_timestamp

        if self.payload_validation_enabled:
            item["mapping"][self.validation_key_attr] = data_record.payload_hash

        now = datetime.datetime.now()
        try:
            # |     LOCKED     |         RETRY if status = "INPROGRESS"                |     RETRY
            # |----------------|-------------------------------------------------------|-------------> .... (time)
            # |             Lambda                                              Idempotency Record
            # |             Timeout                                                 Timeout
            # |       (in_progress_expiry)                                          (expiry)

            # Conditions to successfully save a record:

            # The idempotency key does not exist:
            #    - first time that this invocation key is used
            #    - previous invocation with the same key was deleted due to TTL
            idempotency_record = self._connection.hgetall(data_record.idempotency_key)
            print(idempotency_record)
            if len(idempotency_record) > 0:
                # record already exists.

                # status is completed, so raise exception because it exists and still valid
                if idempotency_record[self.status_attr] == STATUS_CONSTANTS["COMPLETED"]:
                    raise IdempotencyItemAlreadyExistsError

                # checking if in_progress_expiry_attr exists
                # if in_progress_expiry_attr exist, must be lower than now
                if self.in_progress_expiry_attr in idempotency_record and int(
                    idempotency_record[self.in_progress_expiry_attr],
                ) > int(now.timestamp() * 1000):
                    raise IdempotencyItemAlreadyExistsError

            logger.debug(f"Putting record on Redis for idempotency key: {data_record.idempotency_key}")
            self._connection.hset(**item)
            # hset type must set expiration after adding the record
            # Need to review this to get ttl in seconds
            # Q: should we replace self.expires_after_seconds with _get_expiry_timestamp? more consistent
            self._connection.expire(name=data_record.idempotency_key, time=self.expires_after_seconds)
        except redis.exceptions.RedisError:
            raise redis.exceptions.RedisError
        except redis.exceptions.RedisClusterException:
            raise redis.exceptions.RedisClusterException
        except Exception as e:
            logger.debug(f"encountered non-redis exception:{e}")
            raise e

    def _update_record(self, data_record: DataRecord) -> None:
        item: Dict[str, Any] = {}

        item = {
            "name": data_record.idempotency_key,
            "mapping": {
                self.data_attr: data_record.response_data,
                self.status_attr: data_record.status,
            },
        }
        logger.debug(f"Updating record for idempotency key: {data_record.idempotency_key}")
        self._connection.hset(**item)

    def _delete_record(self, data_record: DataRecord) -> None:
        logger.debug(f"Deleting record for idempotency key: {data_record.idempotency_key}")
        # See: https://redis.io/commands/del/
        self._connection.delete(data_record.idempotency_key)
