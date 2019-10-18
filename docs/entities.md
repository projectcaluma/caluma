### Entities

Caluma is split in two parts, form and workflow. The form can be used without a workflow and vice versa, but the full power of Caluma comes when combining the two.

Each part is based on several entities, which usually come in pairs: One defines a "blueprint" and is instance-independent, while the other one represents the blueprint in relation to a specific instance. The two entities are usually connected by a one-to-many relationship, e.g. there can be many concrete `cases` (instance-specific) following a certain `workflow` (global blueprint).

#### Form entities

**Form** defines the structure of a document, basically a collection of questions.

**Question** defines a single input of a form, such as a text, choice or similar. Each question type has a specific representation and validation.

**Document** is a specific instance of a form. Since a form is a collection of questions, a document can be thought of as a collection of answers.

**Answer** contains user input answering a question. There are different answer representations covering different data types.

#### Workflow entities

The naming and concept of workflow entities is inspired by the [Workflow Patterns Initiative](http://www.workflowpatterns.com/).

**Workflow** defines the structure of a business process. It is built up of tasks which are connected by forward-referencing flows.

**Task** is a single action that occurs in a business process.

**Flow** defines the ordering and dependencies between tasks.

**Case** is a specific instance of a workflow. It has an internal state which represents it's progress.

**WorkItem** is a single unit of work that needs to be completed in a specific stage of a case.

#### User entities

User entities are not actual entities on Caluma but provided through authentication token of an OpenID connect provider (see configuration below).

**User** is a human resource which can be part of one or several groups.

**Group** is a collection of users typically a organization.
