import pytest
from minio import Minio, S3Error

from ...caluma_form.models import File, Question


@pytest.mark.parametrize("have_history", [True, False])
def test_delete_file_answer(
    db,
    question_factory,
    answer_factory,
    form_question_factory,
    file_factory,
    form,
    document,
    mocker,
    have_history,
):
    copy = mocker.patch.object(Minio, "copy_object")
    remove = mocker.patch.object(Minio, "remove_object")

    file_question = question_factory(type=Question.TYPE_FILES)
    form_question_factory(question=file_question, form=form)
    answer = answer_factory(question=file_question, value=None, document=document)

    if have_history:
        file_ = answer.files.get()
        file_.rename("new name")
        file_.save()
    assert answer.files.count()  # just checking preconditions
    answer.delete()

    if have_history:
        remove.assert_called()
        copy.assert_called()

    with pytest.raises(File.DoesNotExist):
        answer.files.get()


def test_update_file(db, file_factory, mocker):
    file = file_factory()
    mocker.patch.object(Minio, "copy_object")
    mocker.patch.object(Minio, "remove_object")
    file.name = "something else"
    file.save()
    Minio.copy_object.assert_called()
    Minio.remove_object.assert_called()


@pytest.mark.parametrize("should_raise", [False, True])
def test_missing_file(db, file, mocker, should_raise, answer_factory):
    mocker.patch.object(
        Minio,
        "copy_object",
        side_effect=S3Error(
            code="SomeOtherError" if should_raise else "NoSuchKey",
            message="",
            resource="test_object",
            request_id="",
            host_id="",
            response=None,
        ),
    )

    other_answer = answer_factory()

    if should_raise:
        with pytest.raises(S3Error):
            file.copy(to_answer=other_answer)
    else:
        file.copy(to_answer=other_answer)
