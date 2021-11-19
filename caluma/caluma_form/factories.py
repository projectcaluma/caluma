import faker
from factory import Faker, LazyAttribute, Maybe, SubFactory, lazy_attribute

from ..caluma_core.factories import DjangoModelFactory
from . import models

AUTO_QUESTION_TYPES = [
    t
    for t in models.Question.TYPE_CHOICES
    if t
    not in [
        models.Question.TYPE_STATIC,
        models.Question.TYPE_FORM,
        models.Question.TYPE_DYNAMIC_CHOICE,
        models.Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
        models.Question.TYPE_CALCULATED_FLOAT,
        models.Question.TYPE_ACTION_BUTTON,
    ]
]


class FormFactory(DjangoModelFactory):
    slug = Faker("slug")
    name = Faker("multilang", faker_provider="name")
    description = Faker("multilang", faker_provider="text")
    meta = {}
    is_published = False
    is_archived = False

    class Meta:
        model = models.Form


class QuestionFactory(DjangoModelFactory):
    slug = Faker("slug")
    label = Faker("multilang", faker_provider="name")
    type = Faker("word", ext_word_list=AUTO_QUESTION_TYPES)
    is_required = "true"
    is_hidden = "false"
    configuration = {}
    meta = {}
    is_archived = False
    format_validators = []

    row_form = Maybe(
        "is_table", yes_declaration=SubFactory(FormFactory), no_declaration=None
    )
    sub_form = Maybe(
        "is_form", yes_declaration=SubFactory(FormFactory), no_declaration=None
    )
    static_content = Maybe(
        "is_static",
        yes_declaration=Faker("multilang", faker_provider="text"),
        no_declaration=None,
    )

    # dynamic question
    data_source = Maybe(
        "is_dynamic", yes_declaration="MyDataSource", no_declaration=None
    )

    # calculated float question
    calc_expression = Maybe(
        "is_calc_float", yes_declaration="-1.0", no_declaration=None
    )
    calc_dependents = []

    # action button question
    action = Maybe(
        "is_action_button",
        yes_declaration=Faker("word", ext_word_list=models.Question.ACTION_CHOICES),
        no_declaration=None,
    )
    color = Maybe(
        "is_action_button",
        yes_declaration=Faker("word", ext_word_list=models.Question.COLOR_CHOICES),
        no_declaration=None,
    )
    validate_on_enter = Maybe(
        "is_action_button",
        yes_declaration=False,
        no_declaration=None,
    )

    class Meta:
        model = models.Question

    class Params:
        is_table = LazyAttribute(lambda q: q.type == models.Question.TYPE_TABLE)
        is_form = LazyAttribute(lambda q: q.type == models.Question.TYPE_FORM)
        is_dynamic = LazyAttribute(
            lambda q: q.type
            in [
                models.Question.TYPE_DYNAMIC_CHOICE,
                models.Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
            ]
        )
        is_static = LazyAttribute(lambda q: q.type == models.Question.TYPE_STATIC)
        is_calc_float = LazyAttribute(
            lambda q: q.type == models.Question.TYPE_CALCULATED_FLOAT
        )
        is_action_button = LazyAttribute(
            lambda q: q.type == models.Question.TYPE_ACTION_BUTTON
        )


class OptionFactory(DjangoModelFactory):
    slug = Faker("slug")
    label = Faker("multilang", faker_provider="name")
    is_archived = False
    meta = {}

    class Meta:
        model = models.Option


class QuestionOptionFactory(DjangoModelFactory):
    option = SubFactory(OptionFactory)
    question = SubFactory(QuestionFactory)
    sort = 0

    class Meta:
        model = models.QuestionOption


class FormQuestionFactory(DjangoModelFactory):
    form = SubFactory(FormFactory)
    question = SubFactory(QuestionFactory)
    sort = 0

    class Meta:
        model = models.FormQuestion


class DocumentFactory(DjangoModelFactory):
    form = SubFactory(FormFactory)
    family = None
    meta = {}

    class Meta:
        model = models.Document


class FileFactory(DjangoModelFactory):
    name = Faker("file_name")

    class Meta:
        model = models.File


class AnswerFactory(DjangoModelFactory):
    question = SubFactory(QuestionFactory)
    document = SubFactory(DocumentFactory)
    meta = {}

    @lazy_attribute
    def value(self):
        if (
            self.question.type == models.Question.TYPE_MULTIPLE_CHOICE
            or self.question.type == models.Question.TYPE_DYNAMIC_MULTIPLE_CHOICE
        ):
            return [faker.Faker().name(), faker.Faker().name()]
        elif self.question.type == models.Question.TYPE_FLOAT:
            return faker.Faker().pyfloat()
        elif self.question.type == models.Question.TYPE_INTEGER:
            return faker.Faker().pyint()
        elif self.question.type not in [
            models.Question.TYPE_TABLE,
            models.Question.TYPE_FILE,
            models.Question.TYPE_DATE,
        ]:
            return faker.Faker().name()

        return None

    file = Maybe(
        "is_file", yes_declaration=SubFactory(FileFactory), no_declaration=None
    )
    date = Maybe("is_date", yes_declaration=Faker("date"), no_declaration=None)

    class Meta:
        model = models.Answer

    class Params:
        is_file = LazyAttribute(lambda a: a.question.type == models.Question.TYPE_FILE)
        is_date = LazyAttribute(lambda a: a.question.type == models.Question.TYPE_DATE)


class AnswerDocumentFactory(DjangoModelFactory):
    answer = SubFactory(AnswerFactory)
    document = SubFactory(DocumentFactory)
    sort = 0

    class Meta:
        model = models.AnswerDocument


class DynamicOptionFactory(DjangoModelFactory):
    slug = Faker("slug")
    label = Faker("multilang", faker_provider="name")
    document = SubFactory(DocumentFactory)
    question = SubFactory(QuestionFactory)

    class Meta:
        model = models.DynamicOption
