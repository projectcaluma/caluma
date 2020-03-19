# Workflow WorkItem assignments

When working with a task based system like Caluma, it is important to be able to assign
different roles on a task to specific users/groups. First of all, you want to define who
has to complete a certain task. Depending on the use-case, it's also important to assign
a controlling function to one or more groups for a certain task.

## Assignment types

There three different types of assignments:

| Field                 | Description                                                                                        |
| --------------------- | -------------------------------------------------------------------------------------------------- |
|  `addressed_groups`   | Offer work item to be processed by groups of users, such are not committed to process it though.   |
|  `assigned_users`     | Users responsible to undertake given work item.                                                    |
|  `controlling_groups` | List of groups this work item is assigned to for controlling.                                      |

### `addressed_groups`

Usually the field `addressed_groups` is set by evaluating the Jexl in the
`adress_groups` on the related `Task` instance.

For `WorkItem`s related to a `multipleInstanceTask`, it's possible to manually provide
a list of groups. This is optional and it will fallback to evaluating the
`address_groups` Jexl.

### `assigned_users`

This is a list of manually assigned users that are obliged to complete a `WorkItem`.


### `controlling_groups`

Usually the field `controlling_groups` is set by evaluating the Jexl in the
`control_groups` on the related `Task` instance.

For `WorkItem`s related to a `multipleInstanceTask`, it's possible to manually provide
a list of groups. This is optional and it will fallback to evaluating the
`control_groups` Jexl.

## GroupJexl

The `GroupJexl` is used for avaluating the correct groups for setting
`addressed_groups` and `controlling_groups`.

The simplest form of a valid GroupJexl is a static list of groups:

```
["group1", "group2,]
```

More complex assignments can be achieved with through the `info` object.

### The `info` object in the GroupJexl context

In the `GroupJexl` context, there is an `info` object available. Values inside this object
can be accessed via dot-notation.

This is the structure of the `info` object:

```json
{
    "info": {
        "case": {
            "created_by_group": "str"
        },
        "work_item": {
            "created_by_group": "str"
        },
        "prev_work_item": {
            "controlling_groups": ["str"]
        }
    }
}
```

### Examples

#### Set `controlling_groups` to group that created the `WorkItem`

You want a `Task` whose `WorkItem.controlling_groups` is set to the group that created
the `WorkItem`. For this you set the `control_groups` Jexl to:

`info.work_item.created_by_group`

Beware: this does not work for manually started `WorkItems` from a `multipleInstanceTasks`,
because there we have no previous `WorkItem`.

#### Set `controlling_groups` to group that created the `Case`

This is pretty much the same as the axample above. But instead of using the group that
created the `WorkItem`, we want to use the group that created the `Case`.

`info.case.created_by_group`

#### Controlling `WorkItem`
Let's say you have a work_item `A`, that has group `G` assigned as controlling group.
When the work_item is finished, you want to start a "controlling" work_item `B` addressed to
the controlling group `G` of the work_item `A`.

This can be achieved if you set `address_groups` of the `Task` for `WorkItem` `B` to:

```
info.prev_work_item.controlling_groups
```

This will then correctly evaluate to group `G`.
