INPUT = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "https://example.com/object1660222326.json",
    "type": "object",
    "title": "Sample schema",
    "description": "The root schema comprises the entire JSON document.",
    "examples": [
        {
            "detail": {
                "s3_bucket": "aws-lambda-powertools",
                "s3_key": "event.txt",
                "file_size": 200,
                "file_type": "text/plain",
            }
        }
    ],
    "required": ["detail"],
    "properties": {
        "detail": {
            "$id": "#root/detail",
            "title": "Detail",
            "type": "object",
            "required": ["s3_bucket", "s3_key", "file_size", "file_type"],
            "properties": {
                "s3_bucket": {
                    "$id": "#root/detail/s3_bucket",
                    "title": "The S3 Bucker",
                    "type": "string",
                    "default": "",
                    "examples": ["aws-lambda-powertools"],
                    "pattern": "^.*$",
                },
                "s3_key": {
                    "$id": "#root/detail/s3_key",
                    "title": "The S3 Key",
                    "type": "string",
                    "default": "",
                    "examples": ["folder/event.txt"],
                    "pattern": "^.*$",
                },
                "file_size": {
                    "$id": "#root/detail/file_size",
                    "title": "The file size",
                    "type": "integer",
                    "examples": [200],
                    "default": 0,
                },
                "file_type": {
                    "$id": "#root/detail/file_type",
                    "title": "The file type",
                    "type": "string",
                    "default": "",
                    "examples": ["text/plain"],
                    "pattern": "^.*$",
                },
            },
        }
    },
}
