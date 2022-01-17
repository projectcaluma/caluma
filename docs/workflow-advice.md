# Workflow Advice

This document aims to give some useful advice in regard to dealing with workflows.


## Redo pattern

With the [redo pattern](http://workflowpatterns.com/patterns/resource/detour/wrp34.php)
allows us to redo an already finished work item including all subsequent work items.

> The ability for a resource to redo a work item that has previously been completed in
> a case. Any subsequent work items (i.e. work items that correspond to subsequent tasks
> in the process) must also be repeated.

### Implications

Using this pattern implies the possibility of taking another path in subsequent runs. So
a previously completed work item could stay in the `REDO` state. The `REDO` state on a
work item should, especially in [visibilities](extending.md#visibility-classes) &
[permissions](extending.md#permission-classes), be treated as if the work item
didn't exist.
