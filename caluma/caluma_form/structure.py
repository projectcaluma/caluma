"""Hierarchical representation of a document / form."""
import weakref
from functools import singledispatch
from typing import List, Optional

from .models import AnswerDocument, Question


def object_local_memoise(method):
    def new_method(self, *args, **kwargs):
        if not hasattr(self, "_memoise"):
            self._memoise = {}

        key = str([args, kwargs, method])
        if key in self._memoise:
            return self._memoise[key]
        ret = method(self, *args, **kwargs)
        self._memoise[key] = ret
        return ret

    return new_method


class Element:
    aliases = {}

    def __init__(self, parent=None):
        self._parent = weakref.ref(parent) if parent else None

    def parent(self):
        return self._parent() if self._parent else None

    def children(self):  # pragma: no cover
        return []

    def root(self):
        parent = self.parent()
        if parent:
            return parent.root()
        return self

    def get(self, name, default=None):
        name = self.aliases.get(name, name)

        out = getattr(self, name)

        # if a method is requested, execute it before continuing
        if callable(out):
            out = out()
        if isinstance(out, Element) or isinstance(out, dict):
            return out
        return str(out)


class Field(Element):
    def __init__(self, document, form, question, answer=None, parent=None):
        super().__init__(parent)
        self.document = document
        self.form = form
        self.question = question
        self.answer = answer

    @classmethod
    def factory(cls, document, form, question, answer=None, parent=None):
        if question.type == Question.TYPE_FORM:
            return FieldSet(
                document, form=question.sub_form, question=question, parent=parent
            )
        elif question.type == Question.TYPE_TABLE:
            return RowField(
                document,
                form=question.row_form,
                question=question,
                answer=answer,
                parent=parent,
            )

        return Field(document, form, question, answer, parent=parent)

    def value(self):
        if self.answer is None:
            # no answer object at all - return empty in every case
            return self.question.empty_value()

        elif self.answer.value is not None:
            return self.answer.value

        elif self.question.type == Question.TYPE_TABLE:  # pragma: no cover
            return [
                {cell.question.slug: cell.value() for cell in row.children()}
                for row in self.children()
            ]

        elif self.question.type == Question.TYPE_FILE:
            return self.answer.file

        elif self.question.type == Question.TYPE_DATE:
            return self.answer.date

        elif self.question.type in (
            Question.TYPE_MULTIPLE_CHOICE,
            Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
        ):
            return []

        # no value, no special handling
        return None

    def __repr__(self):
        return f"<Field question={self.question.slug}, value={self.value()} hidden=({self.question.is_hidden}) req=({self.question.is_required})>"


class RowField(Field):
    @object_local_memoise
    def children(self):
        if not self.answer:
            return []  # pragma: no cover

        rows = AnswerDocument.objects.filter(answer=self.answer).order_by("sort")
        return [
            FieldSet(
                ans_doc.document,
                self.question.row_form,
                question=self.question,
                parent=self.parent(),
            )
            for ans_doc in rows
        ]


class FieldSet(Element):
    aliases = {"formMeta": "form_meta"}

    def __init__(self, document, form, question=None, parent=None):
        super().__init__(parent)
        self.document = document
        self.form = form
        self.form_meta = form.meta
        self.question = question
        self._fields = None
        self._sub_forms = None

    @property
    def fields(self):
        if self._fields is None:
            self._fields = {field.question.slug: field for field in self.children()}
        return self._fields

    @property
    def sub_forms(self) -> List[Field]:
        if self._sub_forms is None:
            self._sub_forms = [
                field
                for field in self.children()
                if field.question.type == Question.TYPE_FORM
            ] + [
                child
                for field in self.children()
                for child in field.children()
                if field.question.type == Question.TYPE_TABLE
            ]
        return self._sub_forms

    def get_field(
        self, question_slug: str, check_parent: bool = True
    ) -> Optional[Field]:
        """Collect fields where the question occurs throughout this structure.

        Cases:
        0. question not in structure
        1. question is in the same form (-> greedily returns the question)
        2. question in a neighbor form, ie. answer would be in same document (excluding tables)
        3. question in multiple neighbor forms
        4. question in a table form (same fieldset)
        5. (question in a table form (different row))
        6. question in a table form, lower than current fieldset
        7. question in upper structure (from table row)

        Expected:
        0: return []
        1-3: answer exists once, but might be in multiple forms -> multiple fields
        4: return only row-local fields (not looking up / other rows)
        5: incomplete row missing answer -> return fields with empty value (like case 4)
        6: return all fields for all rows
        7: same as 1-3
        """

        field = self.fields.get(question_slug)

        if field:
            return field

        elif check_parent:
            field = self.parent().get_field(question_slug) if self.parent() else None
            if field:
                return field

        # OK start looking in subforms / row forms below our level.
        # Since we're looking down, we're disallowing recursing to outer context
        # to avoid recursing back to where we are
        for subform in self.sub_forms:
            sub_field = subform.get_field(question_slug, check_parent=False)
            if sub_field:
                return sub_field

        # if we reach this line, we didn't find the question
        return None

    @object_local_memoise
    def children(self):
        answers = {ans.question_id: ans for ans in self.document.answers.all()}
        return [
            Field.factory(
                document=self.document,
                form=self.form,
                question=question,
                answer=answers.get(question.slug),
                parent=self,
            )
            for question in self.form.questions.all()
        ]

    def __repr__(self):
        q_slug = self.question.slug if self.question else None
        if q_slug:
            return f"<FieldSet fq={q_slug}, doc={self.document.pk} hidden=({self.question.is_hidden}) req=({self.question.is_required})>"

        return f"<FieldSet form={self.form.slug}, doc={self.document.pk}>"


def print_document_structure(document):  # pragma: no cover
    """Print a document's structure.

    Intended halfway as an example on how to use the structure
    classes, and a debugging utility.
    """
    ind = {"i": 0}

    @singledispatch
    def visit(vis):
        raise Exception(f"generic visit(): {vis}")

    @visit.register(Element)
    def _(vis):
        print("   " * ind["i"], vis)
        ind["i"] += 1
        for c in vis.children():
            visit(c)
        ind["i"] -= 1

    struc = FieldSet(document, document.form)
    visit(struc)
