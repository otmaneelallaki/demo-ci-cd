def handler(event, context):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/txt"},
        "body": "Template executed properly ! 2222222",
    }
