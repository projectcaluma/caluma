import json

from graphql.error.syntax_error import GraphQLSyntaxError
from graphql.language import parser, visitor

from caluma.caluma_logging.models import AccessLog


class AccessLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # user is available only after the request was processed
        try:
            body = json.loads(request.body.decode("utf-8"))
        except json.decoder.JSONDecodeError:  # pragma: no cover
            return response

        vis = AccessLogVisitor()
        try:
            doc = parser.parse(body["query"])
            visitor.visit(doc, vis)
        except GraphQLSyntaxError:
            pass

        AccessLog.objects.create(
            username=request.user.username,
            query=body.get("query"),
            variables=body.get("variables"),
            status_code=response.status_code,
            has_error=response.status_code >= 400,
            **vis.values,
        )

        return response


class AccessLogVisitor(visitor.Visitor):
    def __init__(self):
        self.values = {}

        super().__init__()

    def enter_operation_definition(self, node, *args):
        # either "query" or "mutation"
        self.values["operation"] = node.operation.value
        try:
            self.values["operation_name"] = node.name.value
        except AttributeError:
            pass

    def enter_selection_set(self, node, *args):
        # grab name of the query, eg. "allCases", which is the first "selection"
        # thus skip any further selections
        if self.values.get("selection"):
            return
        self.values["selection"] = node.selections[0].name.value
