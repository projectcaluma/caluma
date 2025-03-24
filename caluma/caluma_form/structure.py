"""
Structure - Fast and correct form structure representation.

Design requirements:

* Fast initialisation from a document. Use preload if needed to reduce
  number of queries
* Eager loading of a full document structure. No lazy-loading with questionable
  performance expectations
* Correct navigation via question slugs (JEXL references) from any context
* Fast lookups once initialized
* Extensible for caching JEXL expression results

* No properties. Code is always in methods
"""

from __future__ import annotations

import collections
import copy
import itertools
import typing
import weakref
from abc import ABC
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from functools import singledispatch, wraps
from logging import getLogger
from typing import Optional

from caluma.caluma_core import exceptions

if typing.TYPE_CHECKING:  # pragma: no cover
    from caluma.caluma_form.jexl import QuestionJexl

from caluma.caluma_form.models import (
    Answer,
    AnswerDocument,
    Document,
    DynamicOption,
    File,
    Form,
    FormQuestion,
    Option,
    Question,
    QuestionOption,
)

log = getLogger(__name__)


def object_local_memoise(method):
    """Decorate a method to become object-local memoised.

    In other words - The method will cache it's results. If the method is called
    twice with the same arguments, it will return the cached result instead.

    For debugging purposes, you can also set `object_local_memoise.enabled`
    to `False`, which will then behave just as if the memoising didn't happen.
    """

    @wraps(method)
    def new_method(self, *args, **kwargs):
        if not object_local_memoise.enabled:  # pragma: no cover
            # for debugging purposes
            return method(self, *args, **kwargs)
        if not hasattr(self, "_memoise"):
            clear_memoise(self)

        key = str([args, kwargs, method])
        if key in self._memoise:
            object_local_memoise.hit_count += 1
            self._memoise_hit_count += 1
            return self._memoise[key]
        ret = method(self, *args, **kwargs)
        self._memoise_miss_count += 1
        object_local_memoise.miss_count += 1
        self._memoise[key] = ret
        return ret

    return new_method


# This should only be set to `False` for debugging
setattr(object_local_memoise, "enabled", True)

# Statistics - for analysis / debugging
setattr(object_local_memoise, "hit_count", 0)
setattr(object_local_memoise, "miss_count", 0)


def clear_memoise(obj):
    """Clear memoise cache for given object.

    If an object uses the `@object_local_memoise` decorator, you can then
    call `clear_memoise()` on that object to clear all it's cached data.
    """
    obj._memoise = {}
    obj._memoise_hit_count = 0
    obj._memoise_miss_count = 0


class FastLoader:
    """Load everything in a document/form combination as fast as possible.

    The FastLoader is intended to reduce the number of queries as much as
    possible. It uses prefetching and other techniques, and provides fast (dict)
    lookup to any involved entities.

    Note: We treat all keys as strings, even UUIDs. This makes us a bit
    more compatible with various sources of keys.

    While you *can* use the fastloader with any document, it will likely
    load too much if only a sub-document is given
    """

    @classmethod
    def for_document(cls, document):
        new_self = cls()
        new_self._load_document_entities([document.family])
        new_self._load_form_entities(
            set(doc.form_id for doc in new_self._documents.values())
        )
        return new_self

    @classmethod
    def for_queryset(cls, document_qs):
        new_self = cls()
        new_self._load_document_entities(document_qs)
        new_self._load_form_entities(
            set(doc.form_id for doc in new_self._documents.values())
        )
        return new_self

    def __init__(self):
        # Lazy import needed here
        from caluma.caluma_form.jexl import QuestionJexl

        # Evaluator is only used for extracting answer transforms & friends,
        # so is field-independent here
        self._evaluator = QuestionJexl(field=None)

        # Form bits
        self._forms: dict[str, Form] = {}
        self._questions: dict[str, Question] = {}
        self._questions_by_form: dict[str, list[Question]] = defaultdict(list)
        self._question_options: dict[str, list[Option]] = defaultdict(list)
        self._answers_by_document = defaultdict(dict)

        # Document bits
        self._documents: dict[str, Document] = {}
        self._answers: dict[str, Answer] = {}
        self._table_rows_by_answer = defaultdict(list)
        self._answerdocuments: dict[str, AnswerDocument] = {}
        self._files: dict[str, File] = {}
        self._files_by_answer = defaultdict(list)
        self._dynamic_options_by_question = defaultdict(dict)

        # Jexl dependency graph: question(A) -> question(B) -> list of expr type
        # Question B depends on Question A via expression "type". May be multiple types
        # This is "reversed" due to the fact that we mostly need "downstream"
        # updates when updating (recalculating) a field
        self._jexl_dependencies: dict[str, dict[str, str]] = defaultdict(
            lambda: defaultdict(list)
        )

    def _store_question(self, question):
        self._questions[question.pk] = question

        # Build a comprehensive dependency graph for all JEXL expressions
        for expr_property in ["is_hidden", "calc_expression", "is_required"]:
            jexl_expr = getattr(question, expr_property)
            if not jexl_expr or "|" not in str(jexl_expr):
                # not interesting - no transform in the expr
                continue
            # Evaluator is only used for extracting answer transforms & friends,
            # so is field-independent here
            referenced_questions = set(
                itertools.chain(
                    self._evaluator.extract_referenced_questions(jexl_expr),
                    self._evaluator.extract_referenced_mapby_questions(jexl_expr),
                )
            )
            for dependency_slug in referenced_questions:
                self._jexl_dependencies[dependency_slug][question.pk].append(
                    expr_property
                )

    def dependents_of_question(self, slug):
        """Return the dependents of the given question.

        Return format is a dict of question slug -> list-of-dependency-type
        for the given question.

        For example: `question-a` mentions `question-b` in it's `is_hidden`
        expression, then the following call would hold true:

        >>> dependents_of_question('question-b')
        {'question-a': ['is_hidden']}
        """
        return self._jexl_dependencies[slug]

    def _load_form_entities(self, known_forms):
        form_questions = (
            FormQuestion.objects.filter(form__in=known_forms)
            .select_related("question")
            .select_related("form")
            .order_by("-sort")
        )
        choice_questions = []

        collected_forms = set()

        for fq in form_questions:
            if fq.form_id not in self._forms:
                self._forms[fq.form_id] = fq.form

            # This is already pre-sorted, so we can naively append() here
            self._questions_by_form[fq.form_id].append(fq.question)
            self._store_question(fq.question)

            if fq.question.type == Question.TYPE_TABLE:
                collected_forms.add(fq.question.row_form_id)
            if fq.question.type == Question.TYPE_FORM:
                collected_forms.add(fq.question.sub_form_id)

            # Prepare next step - fetch ordered choices
            if fq.question.type in [
                Question.TYPE_CHOICE,
                Question.TYPE_MULTIPLE_CHOICE,
            ]:
                choice_questions.append(fq.question.pk)

        # It could be that the requested forms don't have any questions. We'd still
        # need to add them to our "known" set.
        # TODO: Maybe we can just set *some* value in self._forms, if nobody actually
        # wants to *use* the form objects themselves
        missing_forms = set(known_forms) - set(self._forms)
        if missing_forms:
            for form in Form.objects.filter(slug__in=missing_forms):
                self._forms[form.pk] = form

        if choice_questions:
            already_have_options = set(self._question_options.keys())
            newly_needed = set(choice_questions) - already_have_options
            for qo in (
                QuestionOption.objects.filter(question__in=newly_needed)
                .order_by("-sort")
                .select_related("option")
            ):
                self._question_options[qo.question_id].append(qo.option)

        newly_collected_forms = collected_forms - set(self._forms.keys())
        if newly_collected_forms:
            self._load_form_entities(list(newly_collected_forms))

    def _load_document_entities(self, documents):
        # First: All Documents - These are fetchable via zero JOINs
        if isinstance(documents, list):
            families = [doc.family_id for doc in documents]
        else:
            families = documents.values("family_id")

        self._documents = {
            str(document.pk): document
            for document in Document.objects.filter(family__in=families)
        }
        # Second: All Answers - These are fetchable via zero JOINs, as we
        # already have all the documents
        self._load_answers(self._documents.keys())

        self._answerdocuments = {
            str(answerdocument.pk): answerdocument
            for answerdocument in AnswerDocument.objects.filter(
                # This works, as there should only be the root doc, and any
                # other document in here will be a row doc. So one mismatch,
                # the rest should match just fine
                document__in=self._documents.keys()
            ).order_by("answer_id", "-sort")
        }
        for ad in self._answerdocuments.values():
            self._table_rows_by_answer[str(ad.answer_id)].append(str(ad.document_id))

        # TODO: This uses a JOIN despite us having the answers already loaded.
        # However we don't know the answer's question types yet, so instead of passing
        # a big number of answer ids here (only a few of which will be file answers)
        # we instead use the documents, reducing the number of params, and therefore
        # speeding up the query.
        for file in File.objects.filter(
            answer__document__in=self._documents.keys()
        ).order_by("answer_id", "created_at"):
            self._files_by_answer[str(file.answer_id)].append(file)

        self._load_dynamic_options()

    def _load_answers(self, documents):
        new_answers = {
            str(answer.pk): answer
            for answer in Answer.objects.filter(document__in=documents)
        }
        self._answers.update(new_answers)
        for ans in new_answers.values():
            self._answers_by_document[str(ans.document_id)][ans.question_id] = ans

    def _load_dynamic_options(self):
        for do in DynamicOption.objects.filter(document__in=self._documents):
            self._dynamic_options_by_question[do.question_id][do.slug] = do

    def question_for_answer(self, answer_id):
        ans = self._answers[str(answer_id)]
        return self._questions[ans.question_id]

    def answers_for_document(self, document_id: str) -> dict[str, Answer]:
        """Return an unordered dict of all answers in the given document.

        The resulting dict is keyed by the question slug, pointing to the
        answer object.
        """
        return self._answers_by_document[str(document_id)]

    def files_for_answer(self, answer_id: str) -> list[File]:
        return self._files_by_answer[str(answer_id)]

    def questions_for_form(self, form_id) -> list[Question]:
        return self._questions_by_form[form_id]

    def form_by_id(self, form_id: str) -> Form:
        if form_id not in self._forms:
            log.warning("Fastloader: Form %s was not preloaded - loading now", form_id)
            self._load_form_entities([form_id])
        return self._forms[form_id]

    def rows_for_table_answer(self, answer_id: str) -> list[Document]:
        document_ids = self._table_rows_by_answer[str(answer_id)]
        return [self._documents[doc_id] for doc_id in document_ids]

    def options_for_question(self, question_id):
        return self._question_options[question_id]

    def dynamic_options_for_question(self, question_id):
        return self._dynamic_options_by_question[question_id]


@dataclass
class BaseField(ABC):
    """Base class for the field types. This is the interface we aim to provide."""

    parent: Optional["FieldSet"] = field(default=None)

    question: Optional[Question] = field(default=None)
    answer: Optional[Answer] = field(default=None)

    _fastloader: Optional[FastLoader] = field(default=None)

    def _make_fastloader(self, document):
        return FastLoader.for_document(document)

    @object_local_memoise
    def get_evaluator(self) -> QuestionJexl:
        """Return the JEXL evaluator for this field."""

        # JEXL is implemented such that it has one context in the engine, and
        # trying to swap it out to switch context is just problematic. So we use
        # one JEXL instance per field.

        # deferred import to avoid circular dependency
        from caluma.caluma_form.jexl import QuestionJexl

        # The "info" block is provided by the global context, but we need
        # to patch it to represent some local information:  The "form" and
        # "document" bits should point to the current context, not to the global
        # structure. This is a bit unfortunate, but we *have* to fill this in
        # two separate places to avoid breaking compatibility
        context = collections.ChainMap(
            # We need a deep copy of the global context, so we can
            # extend the info block without leaking
            copy.deepcopy(self.get_global_context()),
            self.get_context(),
        )

        context["info"].update(self.get_local_info_context())

        # Legacy form ref - pointing to the root form. Thinking... can we
        # deprecate this in some reasonable way and let users know without
        # breaking stuff?
        context["form"] = context["info"]["root"]["form"]

        return QuestionJexl(field=self, context=context)

    def get_root(self):
        return self.parent.get_root() if self.parent else self

    @object_local_memoise
    def get_local_info_context(self):
        """Return the dictionary to be used in the local `info` context block.

         Properties (See Ember-Caluma's field source for reference):
         - `form`: Legacy property pointing to the root form.
           -> defined in get_evaluator() as we're only returning `info` here
        * Form information
             - `info.form`: The form this question is attached to.
             - `info.formMeta`: The meta of the form this question is attached to.
             - `info.parent.form`: The parent form if applicable.
             - `info.parent.formMeta`: The parent form meta if applicable.
             - `info.root.form`: The new property for the root form.
             - `info.root.formMeta`: The new property for the root form meta.
        * Case information is taken from the global context
             - `info.case.form`: The cases' form (works for task forms and case forms).
             - `info.case.workflow`: The cases' workflow (works for task forms and case forms).
             - `info.case.root.form`: The _root_ cases' form (works for task forms and case forms).
             - `info.case.root.workflow`: The _root_ cases' workflow (works for task forms and case forms).

        """
        form = self.get_form()

        if parent_info := self.get_parent_fieldset():
            parent_data = {
                "form": parent_info.get_form().slug,
                "formMeta": parent_info.get_form().meta,
            }
        else:
            parent_data = None
        return {
            "question": self.question.slug if self.question else None,
            "form": form and form.slug or None,
            "formMeta": form and form.meta or None,
            "parent": parent_data,
            # TODO how is "root" expected to behave if we're *already* on root?
            "root": self.get_root().get_local_info_context() if self.parent else None,
        }

    def get_parent_fieldset(self):
        """Return the parent fieldset, according to JEXL semantics.

        In JEXL, the parent refers to the next field up that represents another
        form. In Rows for example, this is two levels up, but in regular nested
        forms, it's only one level up.
        """
        my_form = self.get_form()
        p = self.parent
        while p and p.get_form() == my_form:
            p = p.parent
        return p

    @object_local_memoise
    def is_required(self) -> bool:
        """Return True if the field is required.

        Evaluate the `is_required` expression of the field. But if the field
        is hidden, it is considered not-required regardless of what the JEXL
        expression says.
        """

        if self.is_hidden():
            # hidden can never be required
            return False
        if self.all_dependencies_hidden_or_empty(self.question.is_required):
            # All dependencies are hidden, which means we can't calculate
            # the expression at all - assume the field is not required regardless
            # of the expression
            return False

        return self.evaluate_jexl(self.question.is_required)

    @object_local_memoise
    def is_visible(self) -> bool:
        """Just return the opposite of is_hidden() for convenience."""
        return not self.is_hidden()

    @object_local_memoise
    def all_dependencies_hidden_or_empty(self, expr):
        """Check if all dependencies of the expression are hidden or empty.

        Note: If there are no dependencies, we return False. Question slugs
        referring to missing fields are ignored.
        """
        dependencies = list(self.get_evaluator().extract_referenced_questions(expr))
        dep_fields = {
            dep: self.get_field(dep) for dep in dependencies if self.get_field(dep)
        }

        return dep_fields and all(
            # Field missing may be acceptable if it's used in an `answer`
            # transform with a default. Therefore if a field is missing here,
            # we consider it as "empty"/"hidden"
            (field.is_hidden() or field.is_empty()) if field else True
            for field in dep_fields.values()
        )

    @object_local_memoise
    def is_hidden(self, raise_on_error=True) -> bool:
        """Return True if the field is hidden.

        A field is hidden if either it's parent is hidden, or it's `is_hidden`
        JEXL expression evaluates to `True`.
        """
        if self.parent and self.parent.is_hidden():
            # If the parent is hidden, then *we* are implicitly also hidden,
            # without even evaluating our own is_hidden expression
            return True

        if not self.question and not self.parent:
            # Root field is always visible
            return False

        if self.all_dependencies_hidden_or_empty(self.question.is_hidden):
            # All dependencies are hidden, which means we can't calculate
            # the expression at all, and therefore we don't show this field
            # in the form.
            return True

        try:
            return self.evaluate_jexl(self.question.is_hidden, raise_on_error)
        except exceptions.QuestionMissing:
            if raise_on_error:
                # if raise_on_error is False, we ignore this one as well.
                # should be used internally only, for example in get_value()
                raise
            # If the expression fails, we assume an error
            # and consider ourselves as hidden
            return True

    @object_local_memoise
    def slug(self):
        return self.question and self.question.slug or None

    def get_context(self) -> collections.ChainMap: ...

    @object_local_memoise
    def get_field(self, slug) -> BaseField:
        return self.get_context().get(slug)

    @object_local_memoise
    def find_field_by_answer(self, answer) -> BaseField:
        q_field = self.get_field(answer.question_id)
        if q_field and q_field.answer and q_field.answer.pk == answer.pk:
            return q_field

        # answer is not in "our" document, probably we're in a row doc.
        # Therefore, search "everywhere"
        for fld in self.get_root().find_all_fields_by_slug(answer.question_id):
            if fld.answer and fld.answer.pk == answer.pk:
                return fld
        return None

    def refresh(self, answer=None):
        """Refresh this field's answer.

        If an answer is given, use it and update the structure in-place.
        Otherwise, look in the DB.

        Also clear out all the caches on our own field as well as all
        the calc dependents.

        Note: Saving the answer is the caller's responsibility, we only
        update the structure in-memory.
        """
        if answer:
            self.answer = answer
        elif self.answer:
            self.answer.refresh_from_db()
        elif not isinstance(self, FieldSet):
            self.answer = Answer.objects.filter(
                question=self.question, document=self.parent._document
            ).first()

        clear_memoise(self)
        for dep in self._fastloader.dependents_of_question(self.slug()):
            for dep_field in self.get_root().find_all_fields_by_slug(dep):
                dep_field.refresh()

    def calculate(self):
        try:
            return self.evaluate_jexl(self.question.calc_expression)
        except Exception:
            # In calc, if an expression evaluation fails, we just return None.
            # We could be in an unattached table row, for example, and we'd
            # do the recalculation when we're actually being attached.
            return None

    def evaluate_jexl(self, expression: str, raise_on_error=True):
        # Some stupid shortcuts to avoid building up an evaluation context for
        # ~90% of cases where the expression is a simple "true" or "false"
        fast_results = {"true": True, "false": False}
        if (fast_result := fast_results.get(expression)) is not None:
            return fast_result

        eval = self.get_evaluator()

        try:
            return eval.evaluate(expression, raise_on_error)
        except exceptions.QuestionMissing:
            raise
        except Exception as exc:
            log.error(
                f"Error while evaluating expression on question {self.slug()}: "
                f"{expression!r}: {str(exc)}"
            )
            if raise_on_error:
                raise RuntimeError(
                    f"Error while evaluating expression on question {self.slug()}: "
                    f"{expression!r}. The system log contains more information"
                )
            # return None is implied

    def get_global_context(self) -> dict:
        return self._global_context

    @object_local_memoise
    def get_form(self):
        """Return the form in which this field *resides*.

        Note this may be different from the .form property, which for
        fieldsets and rowsets will contain the sub/row form instead.
        """
        parent_form = self.parent.form if self.parent else None
        return parent_form or self.form or None

    def get_path(self):  # pragma: no cover
        """Return a path to the current field.

        The path is a human-readable path to the current field, starting from
        the root. This allows having more context visible
        """

        # This is mainly for debugging
        if not self.parent:
            return "(root)"
        ppath = self.parent.get_path()
        typeinfo = type(self).__name__[0]
        return f"{ppath} -> {typeinfo}:{self.slug()}"


@dataclass
class ValueField(BaseField):
    """Represent a field in the form.

    This is roughly 1:1 with a question, but repeated in case of a table
    row for example.
    """

    # empty string is acceptable
    EMPTY_VALUES = ([], (), {}, None)

    @object_local_memoise
    def get_value(self):
        if self.answer and not self.is_hidden(raise_on_error=False):
            if self.answer.value not in self.EMPTY_VALUES:
                return self.answer.value
            if self.question.type == Question.TYPE_DATE and self.answer.date:
                return self.answer.date
            if self.question.type == Question.TYPE_FILES:
                file_objs = self._fastloader.files_for_answer(self.answer.pk)
                return [f.name for f in file_objs]
        return self.question.empty_value()

    @object_local_memoise
    def get_context(self) -> collections.ChainMap:
        return self.parent.get_context()

    def get_options(self):
        return self._fastloader.options_for_question(self.slug())

    def get_dynamic_options(self):
        """Return the dynamic options for this value.

        Note: These are the dynamic options only, not the full data source
        contents!

        Return a dict of the form slug -> option-object:w

        """
        return self._fastloader.dynamic_options_for_question(self.slug())

    @object_local_memoise
    def is_empty(self):
        if not self.answer:
            return True
        is_date = self.question.type == Question.TYPE_DATE
        is_files = self.question.type == Question.TYPE_FILES
        return (
            # Yeah it's weird - get_value should return empty string if that's
            # what the answer has stored, but is_empty() should treat it as
            # empty, still ¯\_(ツ)_/¯
            not bool(
                (self.answer.value not in (*self.EMPTY_VALUES, ""))
                or (is_date and self.answer.date is not None)
                or (is_files and self.answer.files.exists())
            )
            # Being hidden makes you empty even if an answer exists
            or self.is_hidden()
        )

    def get_global_context(self) -> dict:
        return self.parent.get_global_context()

    def __str__(self):
        return f"Field({self.question.slug}, {self.get_value()})"

    def __repr__(self):
        return f"ValueField(q={self.question.slug}, v={self.get_value()})"


class FieldSet(BaseField):
    def __init__(
        self,
        document,
        form=None,
        parent=None,
        question=None,
        global_context=None,
        _fastloader=None,
    ):
        # TODO: prefetch document once we have the structure built up
        #
        self.question = question
        self._document = document

        self._fastloader = _fastloader or self._make_fastloader(document)
        self.form = form or self._fastloader.form_by_id(document.form_id)

        self._global_context = global_context or {"info": {}}

        # uplinks always weak
        self.parent = weakref.proxy(parent) if parent else None

        self._own_fields = {}

        if parent:
            # Our context is an extension of the parent's context. That way, we can
            # see the fields from the parent context.
            self._context = collections.ChainMap(
                self._own_fields, self.parent.get_context()
            )

            # Extending parent's context with our own: This makes our own fields
            # visible in the parent context as well
            self._extend_root_context(self._own_fields)
        else:
            # Root fieldset
            self._context = collections.ChainMap(self._own_fields)

        self._build_context()

    def _extend_root_context(self, new_map):
        if self.parent:
            self.parent._extend_root_context(new_map)
        else:
            self._context.maps.append(new_map)

    @object_local_memoise
    def is_empty(self):
        # Fieldset: If *any* field is non-empty, we consider ourselves also
        # non-empty.
        # We reverse the lookup here to speed up (don't need to see if *all* are
        # empty, just if *one* has a value)
        if self.is_hidden():
            # Hidden makes us empty, even if there's theoretically a value.
            # We do the "cheap" check first, then iterate over the children.
            return True
        has_at_least_one_value = any(not child.is_empty() for child in self.children())
        return not has_at_least_one_value

    def get_context(self):
        return self._context

    def get_value(self):
        if self.is_empty():
            # is_empty() will return True if we're hidden, so
            # no need to double-check
            return {}
        return {
            formfield.question.slug: formfield.get_value()
            for formfield in self._own_fields.values()
        }

    def is_required(self) -> bool:
        # Fieldsets (in other words - subforms) should never be required,
        # regardless of what their JEXL says
        return False

    def get_all_fields(self) -> Iterable[BaseField]:
        """Return all fields in the structure, as an iterator.

        Yields (slug,field) tuples. But note that a slug may be repeated
        as we iterate over table rows.

        NOTE: For tables, the same *question* may be repeated in each row. This
        is intended and normal behaviour.
        """
        for formfield in self._own_fields.values():
            yield formfield
            if isinstance(formfield, FieldSet):
                yield from formfield.get_all_fields()
            elif isinstance(formfield, RowSet):
                # row sets *must* have fieldsets as children. Let's loop
                # over them here
                for child in formfield.children():
                    yield child
                    yield from child.get_all_fields()

    def find_all_fields_by_slug(self, slug: str) -> list[BaseField]:
        """Return all fields with the given question slug.

        This may return multiple fields, as tables are traversed as well.

        Used for recalculation of calc fields, and other places that may need
        to see all fields for a given question.

        If you need the one field that the `answer` transform would return in
        this context, use `.get_field()` instead.
        """
        result = []
        for formfield in self.get_all_fields():
            if formfield.slug() == slug:
                result.append(formfield)
        return result

    def children(self):
        # This is already sorted, as the context buildup
        # is doing that for us.
        return list(self._own_fields.values())

    def _build_context(self):
        # context inheritance: The ChainMap allows lookups in "parent"
        # contexts, so a row context will be able to look "out". We implement
        # form questions the same way, even though not strictly neccessary

        answers_by_q_slug = self._fastloader.answers_for_document(self._document.pk)

        questions = self._fastloader.questions_for_form(self.form.pk)

        for question in questions:
            if question.type == Question.TYPE_FORM:
                self._context[question.slug] = FieldSet(
                    document=self._document,
                    form=self._fastloader.form_by_id(question.sub_form_id),
                    parent=self,
                    question=question,
                    global_context=self.get_global_context(),
                    _fastloader=self._fastloader,
                )
            elif question.type == Question.TYPE_TABLE:
                self._context[question.slug] = RowSet(
                    question=question,
                    answer=answers_by_q_slug.get(question.slug),
                    parent=self,
                    _fastloader=self._fastloader,
                )
            else:
                # "leaf" question
                self._context[question.slug] = ValueField(
                    question=question,
                    answer=answers_by_q_slug.get(question.slug),
                    parent=self,
                    _fastloader=self._fastloader,
                )

    def __str__(self):
        return f"FieldSet({self.form.slug})"

    def __repr__(self):
        q_slug = self.question.slug if self.question else "(root)"

        return f"FieldSet(q={q_slug}, f={self.form.slug})"

    def print_structure(self, print_fn=None, method=str):  # pragma: no cover
        """Print the structure as a hierarchical list of text.

        You can pass an alternate print function, and also define a custom
        function for turning the fields into text. For example, calling with
        method=repr gives more information than the default method=str.
        """
        return print_structure(self, print_fn, method=method)

    def list_structure(self, method=str):  # pragma: no cover
        """Return the structure as a  list of text, indented.

        You can pass an alternate print function, and also define a custom
        function for turning the fields into text. For example, calling with
        method=repr gives more information than the default method=str.
        """
        return list_structure(self, method)


class RowSet(BaseField):
    rows: list[FieldSet]

    def __init__(
        self, question, parent, answer: Optional[Answer] = None, _fastloader=None
    ):
        self.question = question
        self.answer = answer

        self._fastloader = _fastloader or self._make_fastloader(parent._document)
        self.form = self._fastloader.form_by_id(question.row_form_id)

        if not parent:  # pragma: no cover
            raise exceptions.ConfigurationError(
                f"Table question {self.slug()} has no parent"
            )

        self.parent = weakref.proxy(parent)

        if answer:
            self.rows = [
                FieldSet(
                    document=row_doc,
                    question=question,
                    form=self._fastloader.form_by_id(question.row_form_id),
                    parent=self,
                    global_context=self.get_global_context(),
                    _fastloader=self._fastloader,
                )
                for row_doc in self._fastloader.rows_for_table_answer(answer.pk)
            ]
        else:
            self.rows = []

    def get_value(self):
        if self.is_hidden():  # pragma: no cover
            return []

        return [row.get_value() for row in self.children()]

    @object_local_memoise
    def get_column_questions(self):
        return self._fastloader.questions_for_form(self.form.pk)

    def get_all_fields(self) -> Iterable[BaseField]:
        for row in self.children():
            yield row
            # Row field children are always FieldSets
            yield from row.get_all_fields()

    def get_context(self):
        # Rowset does not have it's own context: Any field within is
        # basically in it's own world (but has a view onto the "outside")
        return self.parent.get_context()

    def children(self):
        return self.rows

    def _extend_root_context(self, new_map):
        # Rowset: We do not recurse further up when extending context,
        # and we're also not updating our own context from the rows
        pass

    @object_local_memoise
    def get_global_context(self) -> dict:
        if not self.parent:  # pragma: no cover
            raise exceptions.ConfigurationError(
                f"Table question {self.slug()} has no parent"
            )

        return self.parent.get_global_context()

    @object_local_memoise
    def is_empty(self):
        # Table is considered empty if it has no rows.
        # Hidden implies empty, even if there *theoretically* is an answer
        # present
        return self.is_hidden() or not bool(self.rows)

    def __str__(self):
        return f"RowSet({self.form.slug})"

    def __repr__(self):
        return f"RowSet(q={self.question.slug}, f={self.form.slug})"


def print_structure(fieldset: FieldSet, print_fn=None, method=str):
    """Print a document's structure.

    Intended halfway as an example on how to use the structure
    classes, and a debugging utility.
    """
    ind = {"i": 0}

    print_fn = print_fn or print

    @singledispatch
    def visit(vis):  # pragma: no cover
        # Should never happen - for completeness only
        raise Exception(f"generic visit(): {vis}")

    @visit.register(FieldSet)
    def _(vis: FieldSet):
        print_fn("   " * ind["i"], method(vis))
        ind["i"] += 1
        for sub in vis.children():
            visit(sub)
        ind["i"] -= 1

    @visit.register(RowSet)
    def _(vis: RowSet):
        print_fn("   " * ind["i"], method(vis))
        ind["i"] += 1
        for sub in vis.children():
            visit(sub)
        ind["i"] -= 1

    @visit.register(ValueField)
    def _(vis):
        print_fn("   " * ind["i"], method(vis))

    visit(fieldset)


def list_structure(fieldset, method=str):
    """List the given fieldset's structure.

    Use the given method (Default: str()) for stringification.
    Return a list of strings, each representing a field in the structure,
    properly indented, useful for visualisation
    """
    out_lines = []

    def fake_print(*args):
        out_lines.append(" ".join([x for x in args]))

    print_structure(fieldset, print_fn=fake_print, method=method)
    return out_lines


def list_document_structure(document, method=str):
    """List the given document's structure.

    Use the given method (Default: str()) for stringification.
    """
    fs = FieldSet(document)
    return list_structure(fs, method)
