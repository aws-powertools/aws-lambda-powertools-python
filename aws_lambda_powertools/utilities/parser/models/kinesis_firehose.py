from datetime import datetime
from typing import List, Optional, Type, Union

from pydantic import BaseModel, validator

from aws_lambda_powertools.shared.functions import base64_decode


class KinesisFirehoseRecordMetadata(BaseModel):
    shardId: str
    partitionKey: str
    approximateArrivalTimestamp: str
    sequenceNumber: str
    subsequenceNumber: str


class KinesisFirehoseRecord(BaseModel):
    data: Union[bytes, Type[BaseModel]]  # base64 encoded str is parsed into bytes
    recordId: str
    approximateArrivalTimestamp: datetime
    kinesisRecordMetadata: Optional[KinesisFirehoseRecordMetadata]

    @validator("data", pre=True, allow_reuse=True)
    def data_base64_decode(cls, value):
        return base64_decode(value)


class KinesisFirehoseModel(BaseModel):
    invocationId: str
    deliveryStreamArn: str
    region: str
    sourceKinesisStreamArn: Optional[str]
    records: List[KinesisFirehoseRecord]
