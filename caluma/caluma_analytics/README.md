# Caluma Analytics

This documentation is aimed at programmers working on the analytics module.
To read about how to use the analytics module, refer to the user docs linked
from the main README.

## General workings / Overall concept

The analytics module's functionality is guided by the "Pivot Table"
feature found in Microsoft Excel and LibreOffice Calc. There are two
steps for a full analysis view:

1) Generate a table of data to be analyzed
2) Apply the pivot table mechanism on selected fields

The queries are  stored as objects in the database, and can be queried
via GraphQL, or via commandline. This way, the module splits into a
design time part and a runtime part, the same as the rest of Caluma.

The two steps mentioned above are reflected in the data model as well.
You can create a "simple table" that doesn't do any aggregation at all.
This table is then used as input to a "pivot table" which runs sums, counts,
averages and so on.

### Simple tables

Simple tables are used to collect data from the production environment.
A simple table consists of one *Starting point*, as well as multiple *fields*.
The starting point defines the entity that will be represented by each row
of the table output. For instance, when using the "Cases" starting point,
each row in the simple table output will represent one case.

Then, there are multiple fields. The fields represent a path to the
information of interest, relative to the starting point. The internal
representation of this field defines how to access the given value.
Each field has a label, and a path in dot-notation, for example
`case.document.answers.total_price`.

### Simple table fields

For example, the `AttributeField` defines how to access an attribute of
a given database table. It could be a `created_at` date field, for example,
or any other field.

When the required data is in another table than the main table, we use a
`JoinField`. This field knows how to SQL `JOIN` the required table.

Each field may have a "parent" field. When generating the SQL for the analysis,
this is used to add it to the correct subquery.

Due to the fact that a simple table row always contains exactly one row
of output per starting object entity, special care must be taken when
extracting data form a 1:N connection (such as work item data from a case):
Since we cannot get multiple work items for the same case, the field
must ensure that only one row of data is returned per "parent-row". This
is done by being explicit in what we select: The workitem path will not only
join the work items, but it needs to take either the first, or the last one,
depending on the user's needs. `workitems[task=ordering,first-by-created]`
and `workitems[task=ordering,last-by-created]` would be two examples
of this.

### Filtering

Each field, when specified on a simple table, may have a filter
associated.  For simplicity's sake, and because we don't have the
full filtering infrastructure of Graphene at our disposal, we only
provide a simple list of values as filtering mechanism: The user can,
at design-time, provide a list of values. Only rows where the value of
the given field matches one of the values will be shown in the output.

## Query generation

When generating queries, we unfortunately cannot use Django's ORM, as the
queries we're generating are too complex, and the output does not match
the ORM's model anyway, so it is of little actual use.

The basic query structure is that we're heavily relying on subqueries, and
join them in the usual manner. When each field is added to the query structure,
we iterate through the field's parents top-down and reuse already-joined tables.
This way, we don't have to join the same data multiple times.

Each `JoinField` defines an inner and outer ref, along the tables and other
conditions that might apply. Those references are used to ensure that the
inner data corresponds to the outer data.
Each subquery is also aliased to a unique name. Subqueries are only reused if
they actually refer to the exact same set of data.

Each query selects all the fields from the inner subquery explicitly by name.
This way, in the outermost query, we have access to all the data from any
subquery. Filtering can thus happen in the outermost query: We cannot do the
filtering in inner queries for the fact that we still want a row in the output
even if one of the fields requested is not available (or NULL). If we did the
filtering "inside", we'd need to use `INNER JOIN`s and would lose this ability.

What if we need to access multiple answers from a form, for example? In this
case, we would generate two distinct subqueries that each retrieves the data
from the "answers" table. The JOIN conditions would be the same, but the inner
condition would differ (namely referring another question id).

### Visibility

Even though we're not using Django's ORM, we still need to respect the
visibilities defined in the Caluma configuration. This is done by fetching a
"plain" queryset from a given model, then filtering it through the visibility
layer. From the resulting queryset, the SQL and parameters are extracted and
used as a basis for the analysis data.


## Code structure

There are a few modules that contain distinct aspects of the code:

* `simple_table.py`: Simple data extraction table, and field definition
* `sql.py`: Generates SQL from the table definitions
* `visibility.py`: Gives us the visibility-filtered querysets
