# FinOps-AWS-Best-Practices
This repository talks about the Best FinOps practices and  Cloud Cost Control approaches  that helps us to reduce the infrastructure maintenances  and focus more on the product development - Keep following this repository for the best content ahead :) ! 

# AWS CloudWatch Log Group Retention Updater

Welcome! This repo contains a simple but powerful Lambda function to help you get a handle on AWS CloudWatch log storage costs. If you’ve ever discovered log groups piling up with “Never Expire” retention, you know how quickly those storage bills can climb—especially across multiple regions.

This tool automatically finds CloudWatch log groups without a set retention policy and changes them to keep logs for 12 months (365 days). It’s a small tweak, but it can make a big difference to your AWS bill over time.

## Why Use This?

- **Stop log bloat:** By default, many log groups keep data forever. That’s rarely needed and gets expensive.
- **Set it and forget it:** This Lambda runs across all your regions and only updates log groups that need it.
- **Visibility:** After each run, you get a report via SNS showing what was updated.

## How It Works

1. The Lambda scans each region you specify for CloudWatch log groups.
2. If it finds a log group with “Never Expire” retention, it updates it to 365 days.
3. It collects a summary of all changes and sends a report to an SNS topic you choose.

## Quick Start

1. **Clone this repo:**
   ```
   git clone https://github.com//aws-cloudwatch-log-retention-updater.git
   cd aws-cloudwatch-log-retention-updater
   ```

2. **Set your SNS topic:**
   Edit `lambda_function.py` and update this line:
   ```
   SNS_TOPIC_ARN = 'arn:aws:sns:::CloudWatchLogs'
   ```
   Replace `` and `` with your AWS details.

3. **Deploy the Lambda:**
   - Zip up the code and upload it to AWS Lambda.
   - Make sure the Lambda role has permissions for:
     - `logs:DescribeLogGroups`
     - `logs:PutRetentionPolicy`
     - `sns:Publish` (for your SNS topic)

4. **(Optional) Schedule it:**
   Use EventBridge (CloudWatch Events) to run this Lambda regularly (daily, weekly, etc.).

## What You’ll Get

After each run, you’ll receive a report like this via SNS:

```
CloudWatch Logs Retention Policy Update Report
Generated on: 2025-06-28 10:00:00 UTC

Log Group Name                              Region       Previous Retention    Updated Retention
-----------------------------------------------------------------------------------------------
/aws/lambda/my-function                     us-west-2    NEVER EXPIRE         365 days
...
Total updated log groups: 5
```

## Permissions

Make sure your Lambda’s IAM role has these permissions:

- logs:DescribeLogGroups
- logs:PutRetentionPolicy
- sns:Publish

## Why 12 Months?

For most teams, 12 months is a sweet spot: long enough for audits and troubleshooting, short enough to keep costs in check. You can always tweak the retention period in the code if you have different needs.

## Contributions

Spot a bug? Want to add features? PRs and issues are welcome!

## License

MIT

**Questions or feedback? Open an issue or drop me a message—happy to help!**
