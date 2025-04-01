from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_iam as iam,
    aws_s3 as s3,
    aws_sns as sns,
    aws_lambda as _lambda,
    aws_s3_notifications as s3_notifications,
    aws_events as events,
    aws_dynamodb as dynamodb,
    aws_events_targets as targets
)
from constructs import Construct

class AgentDocumentAnalysisStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        #crate topic
        topic_chart_creator = sns.Topic(self, "chart-creator", topic_name=f"{self.stack_name}-chart-creator")
        
        #rule eventBridge
        rule_creator = events.Rule(self, "SnsToEcsRule",
            rule_name=f"{self.stack_name}-chart-creator",
            event_pattern={
                "source": ["aws.sns"],
                "detail_type": ["SNS Message"],
                "resources": [topic_chart_creator.topic_arn]
            }
        )

        rule_message = events.Rule(self, "sns-rule-notification",
            rule_name=f"{self.stack_name}-notify-summary",
            event_pattern={
                "source": ["agent.document.analysis"],
                "detail_type": ["summary_notify"]
            }
        )

        table_layer_memory = dynamodb.Table(
            self, f"{self.stack_name}-memory",
            table_name=f"{self.stack_name}-memory",  # Optional: custom name
            partition_key=dynamodb.Attribute(
                name="PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="SK",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST  # On-demand pricing
        )

        table_transaction = dynamodb.Table(
            self, f"{self.stack_name}-transaction",
            table_name=f"{self.stack_name}-transaction",  # Optional: custom name
            partition_key=dynamodb.Attribute(
                name="transactionId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST  # On-demand pricing
        )

        # Optional: add a sort key
        sort_key=dynamodb.Attribute(
            name="createdAt",
            type=dynamodb.AttributeType.STRING
        ),

        # Create IAM role for Lambda functions
        lambda_role_bedrock = iam.Role(
            self, f'{self.stack_name}-lambda-role',
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )

        # Add necessary permissions to the Lambda role
        lambda_role_bedrock.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        
        lambda_role_bedrock.add_to_policy(iam.PolicyStatement(
            actions=["bedrock:InvokeModel","ses:SendEmail"],
            resources=["arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0"]
        ))

        lambda_role_bedrock.add_to_policy(iam.PolicyStatement(
            actions=["ses:SendEmail"],
            resources=["arn:aws:ses:us-east-1:471112847654:identity/gtorresp@bolivariano.com"]
        ))

        lambda_role_bedrock.add_to_policy(iam.PolicyStatement(
            actions=["log:*","cloudwatch:*"],
            resources=["*"]
        ))

        # Add inline policy to the Lambda role
        lambda_role_bedrock.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["s3:GetObject"],
            resources=[f"arn:aws:s3:::bedrock-multimodal-s3/*"]
        ))

        lambda_role_bedrock.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["lambda:GetLayerVersion"],
            resources=[f"arn:aws:lambda:us-east-1:471112847654:layer:numpy_layer:*"]
        ))

        lambda_role_bedrock.add_to_policy(iam.PolicyStatement(
            actions=["dynamodb:GetItem"],
            resources=[table_transaction.table_arn]
        ))

        sns_topic = sns.Topic(self, "FinOpsTopic",
            display_name="AWS FinOps Cost Alerts GT",
            topic_name=f"{self.stack_name}-notify-email"
        )

        lambda_role_bedrock.add_to_policy(iam.PolicyStatement(
            actions=["sns:Publish"],
            resources=[sns_topic.topic_arn, topic_chart_creator.topic_arn]
        ))


        # Define the S3 bucket
        bucket_documents = s3.Bucket(
            self, "documents",
            bucket_name= f"{self.stack_name}-documents",
            versioned=True,  # Enables versioning
            removal_policy= RemovalPolicy.DESTROY,  # Delete on stack deletion
            auto_delete_objects=True  # Delete objects with the stack
        )

        bucket_result_analysis = s3.Bucket(
            self, "result-analysis",
            bucket_name= f"{self.stack_name}-result-analysis",
            versioned=True,  # Enables versioning
            removal_policy= RemovalPolicy.DESTROY,  # Delete on stack deletion
            auto_delete_objects=True  # Delete objects with the stack
        )

        bucket_result_analysis.add_to_resource_policy(
             iam.PolicyStatement(
                actions=[
                    "s3:GetObject"
                ],
                resources=[f"{bucket_result_analysis.bucket_arn}/*"],
                principals=[iam.ArnPrincipal(f"{lambda_role_bedrock.role_arn}"),iam.ServicePrincipal("lambda.amazonaws.com")]
            )
        )


        # The code that defines your stack goes here
        process_document = _lambda.Function(
            self, "process_document",
            function_name= f'{self.stack_name}-process-document',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.process_document",
            environment={
                "BUCKET_NAME": bucket_documents.bucket_name,
                "SNS_TOPIC_EMAIL": sns_topic.topic_arn,
                "MODEL_ID":"anthropic.claude-3-5-sonnet-20240620-v1:0",
                "SNS_TOPIC_CHART_CREATOR":topic_chart_creator.topic_arn,
                "TABLE_TRANSACCION": table_transaction.table_name,
                "TABLE_MEMORY_LAYER": table_layer_memory.table_name
            },
            memory_size=1024,
            role=lambda_role_bedrock,
            timeout=Duration.seconds(90),
            #layers=[matplotlib_layer],
            code=_lambda.Code.from_asset("src/functions/process_document")
        )

        notification_summary = _lambda.Function(
            self, "notification_summary",
            function_name= f'{self.stack_name}-notify-summary',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.notify_summary",
            environment={
                "BUCKET_NAME": bucket_result_analysis.bucket_name,
                "SNS_TOPIC_EMAIL": sns_topic.topic_arn,
                "SNS_TOPIC_CHART_CREATOR":topic_chart_creator.topic_arn,
                "TABLE_TRANSACCION": table_transaction.table_name
            },
            memory_size=1024,
            role=lambda_role_bedrock,
            timeout=Duration.seconds(90),
            code=_lambda.Code.from_asset("src/functions/notify_summary")
        )

        rule_message.add_target(targets.LambdaFunction(notification_summary))
        sns_topic.grant_publish(process_document)
        table_transaction.grant_write_data(process_document)
        table_layer_memory.grant_write_data(process_document)

        # Add S3 event notification (trigger) to invoke Lambda on object creation
        bucket_documents.add_event_notification(
            s3.EventType.OBJECT_CREATED,  # Trigger on new object uploads
            s3_notifications.LambdaDestination(process_document)
        )

        # Grant S3 bucket read permissions to Lambda
        bucket_documents.grant_read(process_document)
        
