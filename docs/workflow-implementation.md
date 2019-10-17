## 2. Implementation

In this chapter, we'll create and execute the example "exam" workflow which has been introduced in the [previous chapter, "Workflow Concepts"](workflow-concepts.md). We'll do so by executing mutations on the Caluma GraphQL API - to get most out of this guide, we recommend to follow along using the interactive GraphiQL console of your local Caluma installation (see the [Getting started guide](https://github.com/projectcaluma/caluma#getting-started) for installation instructions).

### Step 1: Workflow Design

In this first step, we'll create the "exam" workflow including its tasks and flows. Although it would feel most natural to start by creating the workflow itself, we'll start by creating the "fill out exam" task - the reason for this is that when creating a new workflow, we have to tell caluma which task(s) to start when the workflow is started.

#### 1a) Create "fill out exam" task

The following GraphQL snippet runs the `saveSimpleTask` mutation. We have to specify the tasks name and slug - the slug is the technical identifier of the task, and can only contain lower-case letters and a limited set of special characters.

```GraphQL
mutation {
  saveSimpleTask(input: {
    slug: "fill-out-exam",
    name: "Fill out form"
  }) {
    task {
      slug
    }
  }
}
```

After executing the mutation, Caluma should confirm the successful creation of the task with a response like this:

```json
{
  "data": {
    "saveSimpleTask": {
      "task": {
        "slug": "fill-out-exam"
      }
    }
  }
}
```

> **Task types**
>
> _Why did we use the `saveSimpleTask` mutation? There are also other mutations that save tasks._
>
> Caluma supports different types of tasks, each of which has its own set of mutations. The following types are supported:
> - **Simple Tasks** can be completed without any requirements. _Simple_ doesn't mean that they are _easy_ to complete, but that Caluma doesn't (or rather _can't_) do any validations if it's really possible to complete a work item of this type.
>    An example for this type of task might be an "Approval" task in a workflow that includes requests for vacation in a company: The approval can be given without any further information if a given request should be approved.
>
> - **Workflow Form Tasks** and **Task Form Tasks** both deal with forms: Both require a document to be filled out before the task (or, more precisely, it's associated work item) can be completed. Caluma's data model features two places where forms (and therefore documents) can be found:
>
>   TODO diagram
>
>   As you can see, a form can either be attached to a specific task, or to the entire workflow. In the latter case, the form is called the workflow's _main form_.
>
>   _When should I use a Workflow Form instead of a Task Form?_
>
>   Often, workflows have data which is central to their execution: Everyone involved in a specific case needs access to this information in order to work productively with the case. For example, in a workflow involving an application the application form is typically so central that it's used as the workflow's _main form_. On the other hand, if form data is not central to the workflow's "identity", a _task form_ should be used.
>
>   Also note that technically, it would be possible to only use _task forms_ - _workflow forms_ are merely a convenient way to store the most important form data at a central location.
>
> For the first task in our example "exam" workflow, a _workflow form task_ would probably be most appropriate - we decided to use a _simple task_ here anyway, because in this guide we'd like to show workflow concepts without the need to set up a form beforehand.

#### 1b) Create workflow

Now that we have the first task in place, let's create the "exam" workflow:

```GraphQL
mutation {
  saveWorkflow(input: {
    slug: "exam",
    name: "Exam",
    startTasks: ["fill-out-exam"]
  }) {
    workflow {
      slug
    }
  }
}
```

Conceptually, the current state of the workflow looks like this:

TODO diagram

To complete the "exam" workflow according to our specification, we still need to add the second task as well as a _flow_ connecting the two tasks.

#### 1c) Create "correct exam" task

We've already seen how to do this in step 1a - all we need to change is the tasks' name and slug:

```GraphQL
mutation {
  saveSimpleTask(input: {
    slug: "correct-exam",
    name: "Correct exam"
  }) {
    task {
      slug
    }
  }
}
```

#### 1d) Create flow

A _flow_ is a connection between two (or more) tasks in a workflow. Creating a flow looks like this:

```GraphQL
mutation {
  addWorkflowFlow(input: {
    workflow: "exam",
    tasks: ["fill-out-exam"],
    next: "'correct-exam'|task"
  }) {
    workflow {
      flows {
        edges {
          node {
            tasks {
              slug
            }
            next
          }
        }
      }
    }
  }
}
```

```json
{
  "data": {
    "addWorkflowFlow": {
      "workflow": {
        "flows": {
          "edges": [
            {
              "node": {
                "tasks": [
                  {
                    "slug": "fill-out-exam"
                  }
                ],
                "next": "'correct-exam'|task"
              }
            }
          ]
        }
      }
    }
  }
}
```
