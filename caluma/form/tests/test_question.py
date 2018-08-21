import pytest
from graphene.utils.str_converters import to_camel_case

from .. import serializers
from ...schema import schema


@pytest.mark.parametrize("question__is_required", ("true", "true|invalid"))
def test_save_question(db, snapshot, question):
    query = """
        mutation SaveQuestion($input: SaveQuestionInput!) {
          saveQuestion(input: $input) {
            question {
                id
                slug
                label
                type
                configuration
                meta
            }
            clientMutationId
          }
        }
    """

    inp = {
        "input": {
            to_camel_case(key): value
            for key, value in serializers.QuestionSerializer(question).data.items()
        }
    }
    inp["input"]["meta"] = "{}"
    inp["input"]["configuration"] = "{}"
    inp["clientMutationId"] = "test"
    result = schema.execute(query, variables=inp)
    snapshot.assert_match({"data": result.data, "errors": result.errors})
