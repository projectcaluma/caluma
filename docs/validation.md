# Validation

## Javascript Expression Language

Our rationale about using jexl can be found [here](jexl.md).

### Variables available for evaluation

Caluma provides a number of variables to use within JEXL expressions. We assume
that you're familiar with the expression language itself, so we're not
explaining the syntax here.

* `form` refers to the name of the main form of the document. This is useful if
  you use a question in various forms, where it should behave differently. You
  could for example write an expression for `is_required` like this:
  `form == 'building_permit'`. If you use the quesiton in a form named
  "building_permit", it would be required, but if you use it in a form named
  "general_request", it would not be required.

* `info` is a data structure containing information about the document and it's
  form. It's typology is roughly as outlined below. Common access patterns are:

  - `info.root.form` - Same as `form`, gives the root form's slug
  - `info.form` - The direct form where the question resides. Could be a row
    form if the question is within a table, or a FormQuestion's form, etc.
  - `info.parent.form` - The form above the current form. May be useful in
    deeply nested structures.

Note that the `info` object also contains further information about othe
questions and answers, but they're explicitly not for use in JEXL expressions,
and may change without notice.

### Transforms

Transforms are used to turn one type of information into another, similar to
pipes in the unix shell. They can be chained, and may be parametrized as well.

Here are the available transforms:

* `answer`: When applied to a question slug, returns the answer to that question
  in the context of the current document. For example `'your-name'|answer` could
  evaluate to "David". In a `is_required` context, you'll need a boolean value,
  so you could for example use `'your-name'|answer == 'Fred'` in the `is_required`
  field of the "birthday" question, so only Fred needs to tell us his birthday.
* `mapby`: Extract a nested value from a list. Assuming you have a table of
  things currently in the fridge, and you want help the user to decide what to cook:
  `'ravioli' in 'fridge-contents'|answer|mapby('food-name')` will tell you whether
  there are ravioli.
* `debug`: Does not modify the value, but writes the value to the log. This is
  especially useful when you are exploring the data while building forms or
  workflows. The log message may appear in different places depending on
  where it's being run (Browser: console log in the debug tools, Server:
  System or container logs, might depend on your logging configuration)

### Operators

Other operators that aren't transforms are also available:

* `in`: Tells us if a value (left) is contained in a list (right).
* `intersects`: Tells us if two lists have intersecting values.
  In a way, this is a generalized `in` operator. This can be used
  for example in multiple choice questions, as follows:
  To hide questions only relevant for vegetarians or vegans, hide those
  questions by asking some food choices first, then doing this:
  `'food_choices'|answer intersects ['meat', 'fish']` to see if you should
  ask specific questions

## FormatValidators

FormatValidator classes can validate input data for answers, based on rules set on the question.

There are a variety of base FormatValidators ready to use. There is also an [extension
point](extending.md#formatvalidator-classes) for them.

List of built-in base FormatValidators:

* email
* phone-number
