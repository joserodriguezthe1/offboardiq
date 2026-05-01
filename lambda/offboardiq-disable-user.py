import json
import boto3
from datetime import datetime, timezone

iam = boto3.client("iam")

def lambda_handler(event, context):
    print("FULL EVENT:", json.dumps(event))

    action_group = event.get("actionGroup",
"")
    function_name = event.get("function",
"")

    params = {}
    for p in event.get("parameters",
[]):
        params[p[
        "name"
    ]
] = p[
    "value"
]

    employee_id = params.get("employeeId",
"")
    ts = datetime.now(timezone.utc).isoformat()
    actions = []

    if employee_id:
        try:
            iam.delete_login_profile(UserName=employee_id)
            actions.append({
    "action": "delete_login_profile",
    "status": "success"
})
        except iam.exceptions.NoSuchEntityException:
            actions.append({
    "action": "delete_login_profile",
    "status": "skipped"
})
        except Exception as e:
            actions.append({
    "action": "delete_login_profile",
    "status": f"error: {str(e)}"
})

        try:
            keys = iam.list_access_keys(UserName=employee_id)[
    "AccessKeyMetadata"
]
            for key in keys:
                iam.delete_access_key(UserName=employee_id, AccessKeyId=key[
    "AccessKeyId"
])
                actions.append({
    "action": "delete_access_key",
    "status": "success"
})
        except Exception as e:
            actions.append({
    "action": "delete_access_keys",
    "status": f"error: {str(e)}"
})

        try:
            iam.tag_user(UserName=employee_id, Tags=[
    {
        "Key": "OffboardStatus",
        "Value": "access_disabled"
    },
    {
        "Key": "OffboardTimestamp",
        "Value": ts
    }
])
            actions.append({
    "action": "tag_user",
    "status": "success"
})
        except Exception as e:
            actions.append({
    "action": "tag_user",
    "status": f"error: {str(e)}"
})

    body = {
    "employeeId": employee_id,
    "timestamp": ts,
    "actions": actions,
    "summary": f"Access disabled for {employee_id}",
    "rmfControls": [
        "AC-2",
        "PS-4",
        "IA-4"
    ]
}

    response = {
    "messageVersion": "1.0",
    "response": {
        "actionGroup": action_group,
        "function": function_name,
        "functionResponse": {
            "responseBody": {
                "TEXT": {
                    "body": json.dumps(body)
                }
            }
        }
    },
    "sessionAttributes": event.get("sessionAttributes",
    {}),
    "promptSessionAttributes": event.get("promptSessionAttributes",
    {})
}

    print("RESPONSE:", json.dumps(response))
    return response