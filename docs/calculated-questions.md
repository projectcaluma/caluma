# Calculated Questions

Caluma supports the concept of calculated questions, currently only of type
float.  This means we can create a question containing a JEXL expression
(`calcExpression`), for which the answers are automatically generated from said
expression.

Example:
We want to calculate the total costs of an order, which is dependent on a
couple of other answers.  For this we have a question `quantity` which is an
integer, as well as `vat` and a `product-price`.

The resulting `total-price` answer will be calculated from the JEXL expression:
```
'"quantity"|answer * ("product-price"|answer * (1 + "vat"|answer))'
```

### Calculated Answers

The results of calculated questions are of course stored in the corresponding
answers.  As it is highly dependent on the JEXL expression, what kind
dependencies to other questions are created and where in the form (sub-forms,
tables etc.) they are located, it is hard to track when an update of the answer
is needed.  In our generalistic approach, this complexity is mitigated by
evaluating greedly at every possible change.

This leads to behavior that might be unexpected compared to other question
types.

First of all, of course a calculated answer is read-only for the GraphQL (and
python) API.  The answer is fetchable, but there is no
`CreateDocumentCalculated...Answer`.

Second, because the evaluation is greedy, we calculated the answer as soon as
possible, even if referenced answers are missing.  If this is the case, the
answer is still created but will have an empty value.

A couple of mutations act as entrypoints to evaluation of the export and lead
to the creation or update of a calculated answer.
The answer is modified when:
* the calculated question is modified
* the calculated question is added to / removed from a form
* any referenced answer is modified
* a new document for a form containing calculated questions is modified
* a new row document of a row form containing calculated questions is created / deleted


### Limitations

Currently the calculated questions cannot reference other calculated questions. This is an intentional limitation to avoid implementation complexity (dependency calculation "propagation", circular dependency checks).

Additionally only existing questions can be referenced at the time of saving.
This is because of optimizations in the way caluma tracks references of calculated questions.
Specifically, caluma writes the reverse-dependencies to the database at the moment a calculated question is saved.
If a referenced question would be missing at this point, it couldn't memoise the calculated question and thus not update if an answer is created or updated.
