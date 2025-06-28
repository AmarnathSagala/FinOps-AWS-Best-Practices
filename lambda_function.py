import boto3
import json
from datetime import datetime

regions = [
    'us-west-1',
    'us-west-2',
    'eu-west-1',
    'eu-west-2',
    'eu-west-3',
    'eu-south-1',
    'ap-northeast-2',
    'ap-northeast-3',
    'ap-northeast-1',
    'eu-north-1',
    'sa-east-1'
]

RETENTION_DAYS = 365 
SNS_TOPIC_ARN = 'arn:aws:sns:<region>:<account-id>:CloudWatchLogs' # Replace <region> and <account-id> with your AWS details

def update_log_group_retention(region_name):
    logs_client = boto3.client('logs', region_name=region_name)
    paginator = logs_client.get_paginator('describe_log_groups')

    updated_log_groups = []

    for page in paginator.paginate():
        for log_group in page['logGroups']:
            log_group_name = log_group['logGroupName']
            retention = log_group.get('retentionInDays')

            if retention is None:
                try:
                    logs_client.put_retention_policy(
                        logGroupName=log_group_name,
                        retentionInDays=RETENTION_DAYS
                    )
                    updated_log_groups.append([
                        log_group_name,
                        region_name,
                        'NEVER EXPIRE',
                        f'{RETENTION_DAYS} days'
                    ])
                except Exception as e:
                    print(f"[{region_name}] ERROR updating {log_group_name}: {str(e)}")
            else:
                continue  # Skip if retention already set

    return updated_log_groups

def format_output_as_text(all_updates):
    output_content = f"CloudWatch Logs Retention Policy Update Report\n"
    output_content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"

    if all_updates:
        output_content += "{:<60} {:<15} {:<25} {:<25}\n".format("Log Group Name", "Region", "Previous Retention", "Updated Retention")
        output_content += "-" * 130 + "\n"
        for entry in all_updates:
            output_content += "{:<60} {:<15} {:<25} {:<25}\n".format(*entry)
    else:
        output_content += "No log groups needed retention policy updates.\n"

    output_content += f"\nTotal updated log groups: {len(all_updates)}\n"
    return output_content

def publish_to_sns(message, attachment_content):
    sns_client = boto3.client('sns')
    subject = f"CloudWatch Logs Retention Policy Update - {datetime.now().strftime('%Y-%m-%d')}"

    try:
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject=subject,
            MessageAttributes={
                'ReportContent': {
                    'DataType': 'String',
                    'StringValue': attachment_content
                }
            }
        )
        print(f"Successfully published report to SNS topic: {SNS_TOPIC_ARN}")
    except Exception as e:
        print(f"Error publishing to SNS: {str(e)}")

def lambda_handler(event, context):
    all_updates = []

    for region in regions:
        print(f"\n▶ Processing region: {region}")
        region_updates = update_log_group_retention(region)
        all_updates.extend(region_updates)

    if all_updates:
        print("\n📝 Retention Policy Updates:")
        print("{:<60} {:<15} {:<25} {:<25}".format("Log Group Name", "Region", "Previous Retention", "Updated Retention"))
        print("-" * 130)
        for entry in all_updates:
            print("{:<60} {:<15} {:<25} {:<25}".format(*entry))
    else:
        print("✅ No log groups needed retention policy updates.")

    # Format the output for SNS attachment
    report_content = format_output_as_text(all_updates)
    message = f"CloudWatch Logs retention policy update report for {datetime.now().strftime('%Y-%m-%d')}. See detailed report in the message attributes."
    publish_to_sns(message, report_content)

    return {
        'statusCode': 200,
        'updated_count': len(all_updates),
        'message': f"Updated retention on {len(all_updates)} log groups",
    }
