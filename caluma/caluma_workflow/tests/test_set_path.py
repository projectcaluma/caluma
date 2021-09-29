def test_set_paths(db, case, work_item_factory):

    workitem = work_item_factory(case=case)
    # workitem.save()  # trigger the signal
    assert workitem.path == [str(case.pk), str(workitem.pk)]


def test_row_document_path(db, case, form_and_document):
    form, document, questions, answers = form_and_document(
        use_table=True, use_subform=True
    )

    case.document = document
    case.save()
    document.save()
    assert document.path == [str(case.pk), str(document.pk)]

    table_ans = answers["table"]
    row_doc = table_ans.documents.first()
    row_doc.save()
    assert row_doc.path == [str(case.pk), str(document.pk), str(row_doc.pk)]
