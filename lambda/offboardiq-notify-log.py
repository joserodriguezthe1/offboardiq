import json
import boto3
import os
from datetime import datetime, timezone

dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")
SNS_ARN = os.environ.get("SNS_TOPIC_ARN",
"")

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
    summary = params.get("summary", f"Employee {employee_id} offboarded.")
    ts = datetime.now(timezone.utc).isoformat()
    actions = []

    if employee_id:
        try:
            table = dynamodb.Table("OffboardAuditLog")
            table.put_item(Item={
  "employeeId": employee_id,
  "timestamp": ts,
  "eventType": "EMPLOYEE_OFFBOARDED",
  "performedBy": "OffboardIQ-Agent",
  "summary": summary,
  "rmfControls": [
    "AC-2",
    "AU-2",
    "AU-12",
    "PS-4"
  ],
  "status": "COMPLETE"
})
            actions.append({
  "action": "write_audit_log",
  "status": "success"
})
        except Exception as e:
            actions.append({
  "action": "write_audit_log",
  "status": f"error: {str(e)}"
})

        if SNS_ARN:
            try:
                sns.publish(
                    TopicArn=SNS_ARN,
                    Subject=f"[OffboardIQ] Offboarding Complete: {employee_id}",
                    Message=(
                        f"Employee ID : {employee_id}\n"
                        f"Completed   : {ts}\n"
                        f"Agent       : OffboardIQ (Amazon Bedrock)\n\n"
                        f"All IAM access revoked. Evidence report saved to S3.\n"
                        f"RMF Controls: AC-2, PS-4, IA-4, AU-11, AU-12"
                    )
                )
                actions.append({
  "action": "send_sns",
  "status": "success"
})
            except Exception as e:
                actions.append({
  "action": "send_sns",
  "status": f"error: {str(e)}"
})
        else:
            actions.append({
  "action": "send_sns",
  "status": "skipped - no SNS ARN set"
})

    body = {
  "employeeId": employee_id,
  "timestamp": ts,
  "offboardingComplete": True,
  "actions": actions,
  "summary": f"Audit log and notification complete for {employee_id}",
  "rmfControls": [
    "AU-2",
    "AU-12",
    "IR-6"
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