import json

from graphql_relay import to_global_id

from ...caluma_form import models as form_models, schema as form_schema
from .. import permissions, types


class _TestPermission(permissions.BasePermission):
    def permission_impl(self, mutation, info):  # pragma: no cover
        raise NotImplementedError("You need to mock permission_impl")

    @permissions.permission_for(types.Node)
    def has_permission(self, mutation, info):
        # We need this indirection as this method will be registered
        # with the permissions system, but we need to mock the functionality
        # for inspection.
        return self.permission_impl(mutation, info)


def test_get_mutation_params_inline(
    db, schema_executor, permission_classes, form, mocker
):
    permission_classes([f"{__name__}._TestPermission"])

    def check_perm(self, mutation, info):
        params = mutation.get_params(info)
        if mutation == form_schema.SaveTextQuestion:
            return True
        assert len(params) == 1
        assert len(params["input"]) == 2
        assert params["input"]["form"] == form.slug
        meta = json.loads(params["input"]["meta"])
        return meta["allow"]

    mocker.patch(f"{__name__}._TestPermission.permission_impl", check_perm)

    query = r"""
        mutation foo {
            save1: saveDocument(input: {form: "%(form)s", meta: "{\"allow\": true}"})  {
              clientMutationId
            }
            save2: saveDocument(input: {form: "%(form)s", meta: "{\"allow\": false}"})  {
              clientMutationId
            }
            save3: saveTextQuestion(input: {
                slug: "some-question",
                label: "label",
                formatValidators: ["email"]
            }) {
              question {
                id
              }
            }
        }
    """ % {
        "form": form.slug
    }

    result = schema_executor(query)
    assert result.data == {
        "save1": {"clientMutationId": None},
        "save2": None,
        "save3": {
            "question": {
                "id": to_global_id(
                    "TextQuestion", form_models.Question.objects.get().slug
                )
            }
        },
    }
    assert len(result.errors) == 1


def test_get_mutation_params_with_vars(db, schema_executor, permission_classes, mocker):
    permission_classes([f"{__name__}._TestPermission"])

    def check_perm(self, mutation, info):
        params = mutation.get_params(info)
        assert len(params) == 1
        assert len(params["input"]) == 3
        assert params["input"]["slug"] == "email_addr"
        assert type(params["input"]["format_validators"]) is list
        return True

    mocker.patch(f"{__name__}._TestPermission.permission_impl", check_perm)

    query = r"""
        mutation foo ($quest: SaveTextQuestionInput!){
          saveTextQuestion(input: $quest) {
            question {
              id
            }
          }
        }
    """

    result = schema_executor(
        query,
        variable_values={
            "quest": {
                "slug": "email_addr",
                "label": "hello",
                "formatValidators": ["email"],
            }
        },
    )
    assert not result.errors

    assert result.data == {
        "saveTextQuestion": {
            "question": {
                "id": to_global_id(
                    "TextQuestion", form_models.Question.objects.get().slug
                )
            }
        }
    }
