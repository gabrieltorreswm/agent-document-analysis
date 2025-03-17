from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_iam as iam,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_s3_notifications as s3_notifications,
    aws_sqs as sqs,
)
from constructs import Construct

class AgentDocumentAnalysisStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        #Role 
         # Create IAM role for Lambda functions
        lambda_role_bedrock = iam.Role(
            self, f'{self.stack_name}-lambda-role',
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )

          # Add necessary permissions to the Lambda role
        lambda_role_bedrock.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        
        lambda_role_bedrock.add_to_policy(iam.PolicyStatement(
            actions=["bedrock:InvokeModel"],
            resources=["arn:aws:bedrock:us-east-1::foundation-model/*"]
        ))

        # Add inline policy to the Lambda role
        lambda_role_bedrock.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["s3:GetObject"],
            resources=[f"arn:aws:s3:::bedrock-multimodal-s3/*"]
        ))

        # Define the S3 bucket
        bucket_documents = s3.Bucket(
            self, "documents",
            bucket_name= f"{self.stack_name}-documents",
            versioned=True,  # Enables versioning
            removal_policy= RemovalPolicy.DESTROY,  # Delete on stack deletion
            auto_delete_objects=True  # Delete objects with the stack
        )

        # The code that defines your stack goes here
        process_document = _lambda.Function(
            self, "process_document",
            function_name= f'{self.stack_name}-process-document',
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="handler.process_document",
            environment={
                "bucket_documents": bucket_documents.bucket_name
            },
            code=_lambda.Code.from_asset("src/functions/process_document")
        )

        # Add S3 event notification (trigger) to invoke Lambda on object creation
        bucket_documents.add_event_notification(
            s3.EventType.OBJECT_CREATED,  # Trigger on new object uploads
            s3_notifications.LambdaDestination(process_document)
        )

        # Grant S3 bucket read permissions to Lambda
        bucket_documents.grant_read(process_document)
