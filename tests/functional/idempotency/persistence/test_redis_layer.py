# ruff: noqa
import copy
import time as t

import pytest

from aws_lambda_powertools.utilities.idempotency import (
    RedisCachePersistenceLayer,
)
from aws_lambda_powertools.utilities.idempotency.exceptions import (
    IdempotencyAlreadyInProgressError,
    IdempotencyItemAlreadyExistsError,
    IdempotencyItemNotFoundError,
)
from aws_lambda_powertools.utilities.idempotency.idempotency import (
    idempotent,
    idempotent_function,
)


@pytest.fixture
def lambda_context():
    class LambdaContext:
        def __init__(self):
            self.function_name = "test-func"
            self.memory_limit_in_mb = 128
            self.invoked_function_arn = "arn:aws:lambda:eu-west-1:809313241234:function:test-func"
            self.aws_request_id = "52fdfc07-2182-154f-163f-5f0f9a621d72"

        def get_remaining_time_in_millis(self) -> int:
            return 1000

    return LambdaContext()


class MockRedis:
    def __init__(self, decode_responses, cache: dict = None, **kwargs):
        self.cache = cache or {}
        self.expire_dict = {}
        self.decode_responses = decode_responses
        self.acl = {}
        self.username = ""

    def hset(self, name, mapping):
        self.expire_dict.pop(name, {})
        self.cache[name] = mapping

    def from_url(self, url: str):
        pass

    # not covered by test yet.
    def expire(self, name, time):
        if time != 0:
            self.expire_dict[name] = t.time() + time

    # return {} if no match
    def hgetall(self, name):
        if self.expire_dict.get(name, t.time() + 1) < t.time():
            self.cache.pop(name, {})
        return self.cache.get(name, {})

    def get_connection_kwargs(self):
        return {"decode_responses": self.decode_responses}

    def auth(self, username, **kwargs):
        self.username = username

    def delete(self, name):
        self.cache.pop(name, {})

    # return None if nx failed, return True if done
    def set(self, name, value, ex: int = 0, nx: bool = False):
        # expire existing
        if self.expire_dict.get(name, t.time() + 1) < t.time():
            self.cache.pop(name, {})

        if isinstance(value, str):
            value = value.encode()

        # nx logic
        if name in self.cache and nx:
            return None

        self.cache[name] = value
        self.expire(name, ex)
        return True

    # return None if not found
    def get(self, name: str):
        if self.expire_dict.get(name, t.time() + 1) < t.time():
            self.cache.pop(name, {})

        resp = self.cache.get(name, None)

        if resp and self.decode_responses:
            resp = resp.decode("utf-8")

        return resp


@pytest.fixture
def persistence_store_standalone_redis_no_decode():
    redis_client = MockRedis(
        host="localhost",
        port="63005",
        decode_responses=False,
    )
    return RedisCachePersistenceLayer(client=redis_client)


@pytest.fixture
def persistence_store_standalone_redis():
    redis_client = MockRedis(
        host="localhost",
        port="63005",
        decode_responses=True,
    )
    return RedisCachePersistenceLayer(client=redis_client)


def test_idempotent_function_and_lambda_handler_redis_basic(
    persistence_store_standalone_redis: RedisCachePersistenceLayer,
    lambda_context,
):
    mock_event = {"data": "value"}
    persistence_layer = persistence_store_standalone_redis
    expected_result = {"message": "Foo"}

    @idempotent_function(persistence_store=persistence_layer, data_keyword_argument="record")
    def record_handler(record):
        return expected_result

    @idempotent(persistence_store=persistence_layer)
    def lambda_handler(event, context):
        return expected_result

    # WHEN calling the function
    fn_result = record_handler(record=mock_event)
    # WHEN calling lambda handler
    handler_result = lambda_handler(mock_event, lambda_context)
    # THEN we expect the function and lambda handler to execute successfully
    assert fn_result == expected_result
    assert handler_result == expected_result


def test_idempotent_function_and_lambda_handler_redis_cache(
    persistence_store_standalone_redis: RedisCachePersistenceLayer,
    lambda_context,
):
    mock_event = {"data": "value2"}
    persistence_layer = persistence_store_standalone_redis
    result = {"message": "Foo"}
    expected_result = copy.deepcopy(result)

    @idempotent_function(persistence_store=persistence_layer, data_keyword_argument="record")
    def record_handler(record):
        return result

    @idempotent(persistence_store=persistence_layer)
    def lambda_handler(event, context):
        return result

    # WHEN calling the function and handler with idempotency
    fn_result = record_handler(record=mock_event)
    handler_result = lambda_handler(mock_event, lambda_context)
    # THEN we expect the function and lambda handler to execute successfully
    assert fn_result == expected_result
    assert handler_result == expected_result

    result = {"message": "Bar"}
    # Given idempotency record already in Redis
    # When we modified the actual function output and run the second time
    fn_result2 = record_handler(record=mock_event)
    handler_result2 = lambda_handler(mock_event, lambda_context)
    # Then the result should be the same as first time
    assert fn_result2 == expected_result
    assert handler_result2 == expected_result

    # Given idempotency record already in Redis
    # When we modified the actual function output and use a different payload
    mock_event = {"data": "value3"}
    fn_result3 = record_handler(record=mock_event)
    handler_result3 = lambda_handler(mock_event, lambda_context)
    # Then the result should be the actual function output
    assert fn_result3 == result
    assert handler_result3 == result


def test_idempotent_function_and_lambda_handler_redis_basic_no_decode(
    persistence_store_standalone_redis_no_decode: RedisCachePersistenceLayer,
    lambda_context,
):
    # GIVEN redis client passed in has decode_responses=False
    mock_event = {"data": "value-nodecode"}
    persistence_layer = persistence_store_standalone_redis_no_decode
    result = {"message": "Foo"}
    expected_result = copy.deepcopy(result)

    @idempotent_function(persistence_store=persistence_layer, data_keyword_argument="record")
    def record_handler(record):
        return result

    @idempotent(persistence_store=persistence_layer)
    def lambda_handler(event, context):
        return result

    # WHEN calling the function and handler with idempotency
    fn_result = record_handler(record=mock_event)
    handler_result = lambda_handler(mock_event, lambda_context)
    # THEN we expect the function and lambda handler to execute successfully
    assert fn_result == expected_result
    assert handler_result == expected_result

    result = {"message": "Bar"}
    # Given idempotency record already in Redis
    # When we modified the actual function output and run the second time
    fn_result2 = record_handler(record=mock_event)
    handler_result2 = lambda_handler(mock_event, lambda_context)
    # Then the result should be the same as first time
    assert fn_result2 == expected_result
    assert handler_result2 == expected_result

    # Given idempotency record already in Redis
    # When we modified the actual function output and use a different payload
    mock_event = {"data": "value3"}
    fn_result3 = record_handler(record=mock_event)
    handler_result3 = lambda_handler(mock_event, lambda_context)
    # Then the result should be the actual function output
    assert fn_result3 == result
    assert handler_result3 == result


def test_idempotent_lambda_redis_in_progress(
    persistence_store_standalone_redis: RedisCachePersistenceLayer,
    lambda_context,
):
    """
    Test idempotent decorator where lambda_handler is already processing an event with matching event key
    """

    mock_event = {"data": "value4"}
    persistence_store = persistence_store_standalone_redis
    lambda_response = {"foo": "bar"}

    @idempotent(persistence_store=persistence_store)
    def lambda_handler(event, context):
        return lambda_response

    # Given in_progress idempotency record already in Redis
    lambda_handler(mock_event, lambda_context)
    mock_event = {"data": "value7"}
    try:
        persistence_store.save_inprogress(mock_event, 1000)
    except IdempotencyItemAlreadyExistsError:
        pass
    # when invoking with same payload
    # then should raise IdempotencyAlreadyInProgressError
    with pytest.raises(IdempotencyAlreadyInProgressError):
        lambda_handler(mock_event, lambda_context)


def test_idempotent_lambda_redis_delete(
    persistence_store_standalone_redis: RedisCachePersistenceLayer,
    lambda_context,
):
    mock_event = {"data": "test_delete"}
    persistence_layer = persistence_store_standalone_redis
    result = {"message": "Foo"}

    @idempotent(persistence_store=persistence_layer)
    def lambda_handler(event, _):
        return result

    handler_result = lambda_handler(mock_event, lambda_context)
    assert handler_result == result
    # Given the idempotency record from the first run deleted
    persistence_layer.delete_record(mock_event, IdempotencyItemNotFoundError)
    result = {"message": "Foo2"}
    # When lambda hander run for the second time
    handler_result2 = lambda_handler(mock_event, lambda_context)

    # Then lambda handler should return a actual function output
    assert handler_result2 == result
