import pandas as pd


def handler(event, context):

    dic = {"name": ["otmane", "imane"], "prenom": ["chouli", "tribak"]}
    data = pd.DataFrame(dic)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/txt"},
        "body": data,
    }
