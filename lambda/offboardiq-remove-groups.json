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
    removed_groups = []
    removed_policies = []

    if employee_id:
        try:
            for group in iam.list_groups_for_user(UserName=employee_id)[
  "Groups"
]:
                iam.remove_user_from_group(GroupName=group[
  "GroupName"
], UserName=employee_id)
                removed_groups.append(group[
  "GroupName"
])
                actions.append({
  "action": f"remove_group_{group['GroupName']}",
  "status": "success"
})
        except Exception as e:
            actions.append({
  "action": "remove_groups",
  "status": f"error: {str(e)}"
})

        try:
            for policy in iam.list_attached_user_policies(UserName=employee_id)[
  "AttachedPolicies"
]:
                iam.detach_user_policy(UserName=employee_id, PolicyArn=policy[
  "PolicyArn"
])
                removed_policies.append(policy[
  "PolicyName"
])
                actions.append({
  "action": f"detach_{policy['PolicyName']}",
  "status": "success"
})
        except Exception as e:
            actions.append({
  "action": "detach_policies",
  "status": f"error: {str(e)}"
})

        try:
            for pname in iam.list_user_policies(UserName=employee_id)[
  "PolicyNames"
]:
                iam.delete_user_policy(UserName=employee_id, PolicyName=pname)
                actions.append({
  "action": f"delete_inline_{pname}",
  "status": "success"
})
        except Exception as e:
            actions.append({
  "action": "delete_inline_policies",
  "status": f"error: {str(e)}"
})

    body = {
  "employeeId": employee_id,
  "timestamp": ts,
  "removedGroups": removed_groups,
  "removedPolicies": removed_policies,
  "actions": actions,
  "summary": f"Groups and policies removed for {employee_id}",
  "rmfControls": [
    "AC-2",
    "AC-3",
    "PS-4"
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