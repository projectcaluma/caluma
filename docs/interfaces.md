# Interfaces

Here you find a list of interfaces we support and won't change without further notice.

## The `info` object

The `info` object holds the resolver info.

- `info.context` holds the [http request](https://docs.djangoproject.com/en/1.11/ref/request-response/#httprequest-objects)
- `info.context.user` holds the `User`

## Models

We can't guarantee stability for whole models. However certain fields are considered stable.
Changes in non-guaranteed fields won't receive prominent mention in release notes, for example,
and won't trigger a major version bump (according to semver).

For more information about a model and it's fields, please consult the source code.

### General

All models share a common set of fields:

- `created_at`
- `modified_at`
- `created_by_user`
- `created_by_group`
- `history` --> manager for accessing historical records

### caluma_form.models.Form

This model contains the forms.

#### Fields

- `slug` / `pk`
- `name`
- `description`
- `meta`
- `is_published`
- `is_archived`
- `questions`
- `source`

### caluma_form.models.Question

This model contains the questions.

#### Fields

- `slug` / `pk`
- `label`
- `type`
- `is_required`
- `is_hidden`
- `is_archived`
- `placeholder`
- `info_text`
- `static_content`
- `configuration`
- `meta`
- `data_source`
- `options`
- `row_form`
- `sub_form`
- `source`
- `format_validators`

#### Properties

- `min_length`
- `max_length`
- `max_value`
- `min_value`

### caluma_form.models.FormQuestion

Intermediary table for the `Form` <--> `Question` m2m.

#### Fields

- `id` / `pk`
- `form`
- `question`
- `sort`

### caluma_form.models.Option

This model contains the options used in choice and mutliple choice questions.

#### Fields

- `slug` / `pk`
- `label`
- `is_archived`
- `meta`
- `source`

### caluma_form.models.QuestionOption

Intermediary table for the `Question` <--> `Option` m2m.

#### Fields

- `id` / `pk`
- `question`
- `option`
- `sort`

### caluma_form.models.Document

This model contains the documents.

#### Fields

- `id` / `pk`
- `family`
- `form`
- `meta`

### caluma_form.models.Answer

This model contains the answers.

#### Fields

- `id` / `pk`
- `question`
- `value`
- `meta`
- `document`
- `documents`
- `date`
- `file`

### caluma_form.models.AnswerDocument

Intermediary table for the `Answer` <--> `Document` m2m used in table answers.

#### Fields

- `id` / `pk`
- `answer`
- `document`
- `sort`

### caluma_form.models.File

This model contains the file records used in file answers.

#### Fields

- `id` / `pk`
- `name`

#### Properties

- `object_name`
- `upload_url`
- `download_url`
- `metadata`

### caluma_workflow.models.Task

This model contains tasks.

#### Fields

- `slug` / `pk`
- `name`
- `description`
- `type`
- `meta`
- `address_groups`
- `control_groups`
- `is_archived`
- `form`
- `lead_time`
- `is_multiple_instance`

#### Methods

- `calculate_deadline()`

### caluma_workflow.models.Workflow

This model contains workflows.

#### Fields

- `slug` / `pk`
- `name`
- `description`
- `meta`
- `is_published`
- `is_archived`
- `start_tasks`
- `allow_all_forms`
- `allow_forms`

#### Properties

- `flows`

### caluma_workflow.models.Flow

This model contains flows.

#### Fields

- `id` / `pk`
- `next`

### caluma_workflow.models.TaskFlow

This model contains task flows.

#### Fields

- `id` / `pk`
- `workflow`
- `task`
- `flow`

### caluma_workflow.models.Case

This model contains cases.

#### Fields

- `id` / `pk`
- `closed_at`
- `closed_by_user`
- `closed_by_group`
- `workflow`
- `status`
- `meta`
- `document`

### caluma_workflow.models.WorkItem

This model contains work items.

#### Fields

- `id` / `pk`
- `closed_at`
- `closed_by_user`
- `closed_by_group`
- `deadline`
- `task`
- `status`
- `meta`
- `addressed_groups`
- `controlling_groups`
- `assigned_users`
- `case`
- `child_case`
- `document`

### caluma_user.models.OIDCUser / caluma_user.models.AnonymousUser

The user models are special in Caluma, as they are not stored in the database, but only
available during the lifetime of a request.

#### Fields

- `claims`
- `username`
- `groups`
- `token`
- `is_authenticated`

#### Properties

- `group`

## Schema

All the schemas:

- `caluma_data_source.schema`
- `caluma_form.schema`
- `caluma_workflow.schema`

## urls.py

You can include the `graphql` endpoint into your `urls.py` from `caluma.caluma_core.urls`.

## Extensions base classes and decorators

Further information about extensions and their utilities can be found [here](extending.md).

For completeness, they are listed here:

- `caluma_core.mutation.Mutation`
- `caluma_core.permissions.AllowAny`
- `caluma_core.permissions.BasePermission`
- `caluma_core.permissions.object_permission_for`
- `caluma_core.permissions.permission_for`
- `caluma_core.validations.BaseValidation`
- `caluma_core.validations.validation_for`
- `caluma_core.visibilities.Any`
- `caluma_core.visibilities.BaseVisibility`
- `caluma_core.visibilities.filter_queryset_for`
- `caluma_core.visibilities.Union`
- `caluma_data_source.data_source.BaseDataSource`
- `caluma_data_source.utils.data_source_cache`
- `caluma_user.permissions.CreatedByGroup`
- `caluma_user.permissions.IsAuthenticated`
- `caluma_user.visibilities.Authenticated`
- `caluma_user.visibilities.CreatedByGroup`
- `caluma_workflow.visibilities.AddressedGroups`

## Public Python API

You can also use the full business logic that is provided by the GraphQL API
in your application that installs Caluma as a django app:

- `caluma_form.api.save_answer` To save an answer for give question, document
- `caluma_form.api.save_document` To save an document
- `caluma_workflow.api.start_case` To start a new case of a given workflow
- `caluma_workflow.api.cancel_case` To cancel a case
- `caluma_workflow.api.suspend_case` To suspend a case
- `caluma_workflow.api.resume_case` To resume a case
- `caluma_workflow.api.complete_work_item` To complete a work item
- `caluma_workflow.api.skip_work_item` To skip a work item
- `caluma_workflow.api.cancel_work_item` To cancel a work item
- `caluma_workflow.api.suspend_work_item` To suspend a work item
- `caluma_workflow.api.resume_work_item` To resume a work item
