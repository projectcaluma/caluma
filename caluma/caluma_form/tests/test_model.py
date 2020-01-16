import pytest
from minio import Minio

from ...caluma_form.models import File, Question


def test_delete_file_answer(
    db,
    question_factory,
    answer_factory,
    form_question_factory,
    file_factory,
    form,
    document,
    mocker,
):
    file_question = question_factory(type=Question.TYPE_FILE)
    form_question_factory(question=file_question, form=form)
    answer = answer_factory(
        question=file_question, value=None, document=document, file=file_factory()
    )
    mocker.patch.object(Minio, "copy_object")
    mocker.patch.object(Minio, "remove_object")
    answer.delete()
    with pytest.raises(File.DoesNotExist):
        answer.file.refresh_from_db()


def test_update_file(db, file_factory, mocker):
    file = file_factory()
    mocker.patch.object(Minio, "copy_object")
    mocker.patch.object(Minio, "remove_object")
    file.name = "something else"
    file.save()
    Minio.copy_object.assert_called()
    Minio.remove_object.assert_called()
