"""Hierarchical representation of a document / form."""
import weakref
from functools import singledispatch
from typing import Optional

from .models import Question


def object_local_memoise(meth):
    def new_meth(self, *args, **kwargs):
        if not hasattr(self, "_memoise"):
            self._memoise = {}

        key = str([args, kwargs, meth])
        if key in self._memoise:
            return self._memoise[key]
        ret = meth(self, *args, **kwargs)
        self._memoise[key] = ret
        return ret

    return new_meth


class Element:
    def __init__(self, parent=None):
        self._parent = weakref.ref(parent) if parent else None

    def parent(self):
        return self._parent() if self._parent else None

    def children(self):  # pragma: no cover
        return []


class AnsQuestion(Element):
    def __init__(self, document, form, question, answer=None, parent=None):
        super().__init__(parent)
        self.document = document
        self.form = form
        self.question = question
        self.answer = answer

    @classmethod
    def factory(cls, document, form, question, answer=None, parent=None):
        if question.type == Question.TYPE_FORM:
            return DocForm(
                document, form=question.sub_form, question=question, parent=parent
            )
        elif question.type == Question.TYPE_TABLE:
            return RowAnsQuestion(
                document,
                form=question.row_form,
                question=question,
                answer=answer,
                parent=parent,
            )

        return AnsQuestion(document, form, question, answer, parent=parent)

    def ans_value(self):
        if self.answer is None:
            # no answer object at all - return empty in every case
            return self.question.empty_value()

        if self.answer.value is not None:
            return self.answer.value

        elif self.question.type == Question.TYPE_TABLE:
            return [
                {cell.question.slug: cell.ans_value() for cell in row.children()}
                for row in self.children()
            ]
        elif self.question.type == Question.TYPE_FORM:
            # forms never have values themselves
            return None
            return [
                {cell.question.slug: cell.ans_value() for cell in row.children()}
                for row in self.children()
            ]

    def __repr__(self):
        return f"<AnsQuestion question={self.question.slug}, value={self.ans_value()} hidden=({self.question.is_hidden}) req=({self.question.is_required})>"


class RowAnsQuestion(AnsQuestion):
    @object_local_memoise
    def children(self):
        if not self.answer:
            return []

        return [
            DocForm(
                row_doc,
                self.question.row_form,
                question=self.question,
                parent=self.parent(),
            )
            for row_doc in self.answer.documents.all()
        ]


class DocForm(Element):
    def __init__(self, document, form, question=None, parent=None):
        super().__init__(parent)
        self.document = document
        self.form = form
        self.question = question
        self._ans_questions = None
        self._sub_forms = None

    def ans_value(self):
        return None

    def _build_ans_questions(self):
        if self._ans_questions is None:
            self._ans_questions = {aq.question.slug: aq for aq in self.children()}
        if self._sub_forms is None:
            self._sub_forms = {
                aq.question.slug: aq
                for aq in self.children()
                if aq.question.type == Question.TYPE_FORM
            }

    def get_ans_question(
        self, question_slug: str, allow_check_parent: bool = True
    ) -> Optional[AnsQuestion]:

        self._build_ans_questions()

        ans_question = self._ans_questions.get(question_slug)

        if not ans_question and allow_check_parent:
            ans_question = (
                self.parent().get_ans_question(question_slug) if self.parent() else None
            )
        if ans_question:
            return ans_question

        # OK start looking in subforms / row forms below our level.
        # Since we're looking down, we're disallowing recursing to outer context
        # to avoid recursing back to where we are
        for subform in self._sub_forms.values():
            sub_aq = subform.get_ans_question(question_slug, allow_check_parent=False)
            if sub_aq:
                return sub_aq
        # if we reach this line, we didn't find the question
        return None

    @object_local_memoise
    def children(self):
        answers = {ans.question_id: ans for ans in self.document.answers.all()}
        return [
            AnsQuestion.factory(
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
            return f"<DocForm fq={q_slug}, doc={self.document.pk} hidden=({self.question.is_hidden}) req=({self.question.is_required})>"

        return f"<DocForm form={self.form.slug}, doc={self.document.pk}>"


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

    struc = DocForm(document, document.form)
    visit(struc)
