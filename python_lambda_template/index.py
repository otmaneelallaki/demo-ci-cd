import pandas as pd


def handler(event, context):
    # Create a DataFrame
    data = {"Name": ["Alice", "Bob", "Charlie"], "Age": [30, 35, 40]}
    df = pd.DataFrame(data)

    # Convert DataFrame to JSON string
    df_json = df.to_json(orient="records")

    return {"statusCode": 200, "body": df_json, "headers": {"Content-Type": "application/json"}}
