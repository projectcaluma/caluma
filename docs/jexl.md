# Javascript Expression Language

Caluma relies on Javascript Expression Language alias
[JEXL](https://github.com/TomFrost/Jexl) for defining powerful yet simple
expressions for complex validation and flow definitions. Reason for
using JEXL over other languages is that it can be simply implemented
in the backend and frontend as of its defined small scope. This allows
frontends in the browser to validate data in exactly the same way as
the server will, while not limiting validation to simple regexes.

This speeds up user interaction a good deal. JEXL expressions are used in
the following contexts:

* Deciding whether a field should be visible or not (`is_hidden` property)
* Deciding whether a field is required (`is_required` property)
* Deciding what groups should be addressed in a `WorkItem`
* Deciding what groups should have a controlling function on a `WorkItem`
* Deciding what `Task` should be used for the next `WorkItem`

Within the expressions, you can access various information about the context.

Specific information about the usage of jexl expression can be found in their respective documentation:

* [Document validation](validation.md)
* [Workflow WorkItem assignments](workflow-workitem-assignments.md)
