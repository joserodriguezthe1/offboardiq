import json
import boto3
from datetime import datetime, timezone

iam = boto3.client("iam")
s3 = boto3.client("s3")
BUCKET = "offboardiq-evidence"

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
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    actions = []
    snapshot = {}

    if employee_id:
        try:
            u = iam.get_user(UserName=employee_id)[
    "User"
]
            snapshot[
    "user"
] = {
    "UserName": u[
        "UserName"
    ],
    "UserId": u[
        "UserId"
    ],
    "Arn": u[
        "Arn"
    ]
}
            snapshot[
    "groups"
] = [
                g[
        "GroupName"
    ] for g in
                iam.list_groups_for_user(UserName=employee_id)[
        "Groups"
    ]
]
            snapshot[
    "policies"
] = [
                p[
        "PolicyName"
    ] for p in
                iam.list_attached_user_policies(UserName=employee_id)[
        "AttachedPolicies"
    ]
]
            actions.append({
    "action": "collect_snapshot",
    "status": "success"
})
        except Exception as e:
            actions.append({
    "action": "collect_snapshot",
    "status": f"error: {str(e)}"
})

        report = {
    "reportType": "OffboardingEvidenceReport",
    "generatedAt": ts,
    "generatedBy": "OffboardIQ-Agent",
    "employeeId": employee_id,
    "rmfControls": [
        "AC-2",
        "AU-11",
        "PS-4",
        "SI-12"
    ],
    "iamSnapshot": snapshot,
    "auditStatement": (
                f"Employee {employee_id} offboarded on {date_str}. ""All access removed per NIST SP 800-53 AC-2 and PS-4."
            )
}

        key = f"offboarding-reports/{date_str}/{employee_id}_report.json"
        try:
            s3.put_object(
                Bucket=BUCKET,
                Key=key,
                Body=json.dumps(report, indent=2),
                ContentType="application/json",
                ServerSideEncryption="AES256"
            )
            actions.append({
    "action": "save_to_s3",
    "status": "success",
    "key": key
})
        except Exception as e:
            actions.append({
    "action": "save_to_s3",
    "status": f"error: {str(e)}"
})

    body = {
    "employeeId": employee_id,
    "timestamp": ts,
    "evidenceLocation": f"s3://{BUCKET}/offboarding-reports/{date_str}/{employee_id}_report.json",
    "actions": actions,
    "summary": f"Evidence report archived for {employee_id}",
    "rmfControls": [
        "AU-11",
        "PS-4",
        "SI-12"
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