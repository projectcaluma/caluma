# GraphQL

As noted before, Caluma uses a GraphQL API for communication between
frontends, other services, and the Caluma service itself.

The easiest way to get to know Caluma's data
structures is to start the service and navigate to
[localhost:8000/graphql/](http://localhost:8000/graphql/) (assuming you
have the development server running).

## Relay

On top of GraphQL, we use [relay's way of specifying nodes and edges
](https://facebook.github.io/relay/graphql/connections.htm) to further
structurise the interface.


## Filtering, ordering and searching

We're currently in a transition phase of cleaning up our filtering interface.
There are various filters, for example on `allDocuments`:

> **Note:** We're phasing out this old-style filtering some time in the future.
> If you have code that uses this format, please rewrite your queries to the
> syntax described below.


### Old-Style filtering (Deprecated!)

```graphql
query foo {
  allDocuments(hasAnswer: {question: "foo", value: "bar"}) {
    edges {
       node {
        id
      }
    }
  }
}
```

However, this syntax is rather inflexible: In some cases, you may need to filter
by excluding things, and sometimes, you may want to filter documents by multiple
`hasAnswer` queries. This is not possible with the above syntax.

Therefore, we have invented a new way to do things. It uses the same filters,
but they are now called differently:


### New-Style filtering

The new filtering syntax uses just one `filter` keyword. It accepts a list of
filter objects that allow the same syntax as before. The above query would now
be written like this:

```graphql
query foo {
  allDocuments(filter: [
    {hasAnswer: {question: "foo", value: "bar"}}
  ]) {
    edges {
       node {
        id
      }
    }
  }
}
```

How does this help? Well, you can now use the same filter type twice in the same
query, filtering for different things! The following query is totally legal and
functional. And because we can, there's now an optional argument `invert:true`
as well, so you can exclude records that you don't want!

```graphql
query foo {
  allDocuments(filter: [
    {hasAnswer: {question: "foo", value: "bar"}},
    {hasAnswer: {question: "baz", value: "hello"}, invert:true}
  ]) {
    edges {
       node {
        id
      }
    }
  }
}
```

So the above query would return all documents that have a question named "foo"
with the value "bar", but exclude all documents from that list where another
question "baz" has the value "hello".

#### Sorting

The ordering/sorting functionality is also separated from filtering in a
syntactic manner. This allows us to do "chained" ordering, for example
sorting by field A, and if the values are equal, sorting by field B as
well (potentially in another direction).

For example, if you have documents whose form has a "first-name" and
"last-name" question, you could do the following to sort by last name
first, and then backwards by first name:

```graphql
query foo {
  allDocuments(
    filter: [ ... ],
    order: [
      {answerValue: "last-name",  direction:ASC},
      {answerValue: "first-name", direction:DESC}
    ]
  ) {
     ...
  }
}
```
