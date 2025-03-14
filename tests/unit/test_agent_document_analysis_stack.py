import aws_cdk as core
import aws_cdk.assertions as assertions

from agent_document_analysis.agent_document_analysis_stack import AgentDocumentAnalysisStack

# example tests. To run these tests, uncomment this file along with the example
# resource in agent_document_analysis/agent_document_analysis_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AgentDocumentAnalysisStack(app, "agent-document-analysis")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
