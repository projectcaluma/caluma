# Calculated Questions

Caluma supports the concept of calculated questions, currently only of type float.
This means we can create a question containing a JEXL expression (`calcExpression`), for which the answers are automatically generated from said expression.

Example:
We want to calculate the total costs of an order, which is dependent on a couple of other answers.
For this we have a question `quantity` which is an integer, as well as `vat` and a `product-price`.

The resulting `total-price` answer will be calculated from the JEXL expression:
```
'"quantity"|answer * ("product-price"|answer * (1 + "vat"|answer))'
```

### Implementation

This feature makes heavy use of Django signals. There are two "main loops" for this.


#### `calcDependents`

Every question that is referenced in a `calcExpression` will memoize the referencing calculated question.
This list of calculation dependents is mutated whenever a calculated question is created, updated or deleted.

#### Calculated Answers

The results of calculated questions are of course stored in the corresponding answers.
As it is highly dependent on JEXL expression, what kind dependencies to other questions are created and where in the form (sub-forms, tables etc.) they are located.
In our generalistic approach, this complexity is mitigated by evaluating greedly at every possible change.

This leads to behavior that might be unexpected compared to other question types.

First of all, of course a calculated answer is read-only for the GraphQL (and python) API.
The answer is fetchable, but there is no `CreateDocumentCalculated...Answer`.

A couple of mutation lead to the creation or update of a calculated answer.
The answer is modified when:
* the calculated question is modified
* the calculated question is added to / removed from a form.
* any referenced answer is modified
* a new document for a form containing calculated questions is modified
* a new row document of a row form containing calculated questions is created / deleted


### Limitations

The current approach has some limitations that stem from compromises in the calculation of answers.

* 1. calculated questions cannot reference other calculated questions
* 2. calculated questions can only reference questions that are on the same form-level or lower
