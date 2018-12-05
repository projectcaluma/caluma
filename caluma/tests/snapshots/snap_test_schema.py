# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots[
    "test_schema_introspect 1"
] = """schema {
  query: Query
  mutation: Mutation
}

input AddFormQuestionInput {
  form: ID!
  question: ID!
  clientMutationId: String
}

type AddFormQuestionPayload {
  form: Form
  clientMutationId: String
}

input AddWorkflowFlowInput {
  workflow: ID!
  task: ID!
  next: FlowJexl!
  clientMutationId: String
}

type AddWorkflowFlowPayload {
  workflow: Workflow
  clientMutationId: String
}

interface Answer {
  id: ID
  createdAt: DateTime!
  createdByUser: String
  createdByGroup: String
  modifiedAt: DateTime!
  question: Question!
  meta: JSONString!
}

type AnswerConnection {
  pageInfo: PageInfo!
  edges: [AnswerEdge]!
}

type AnswerEdge {
  node: Answer
  cursor: String!
}

enum AnswerOrdering {
  CREATED_AT_ASC
  CREATED_AT_DESC
  MODIFIED_AT_ASC
  MODIFIED_AT_DESC
  CREATED_BY_USER_ASC
  CREATED_BY_USER_DESC
  CREATED_BY_GROUP_ASC
  CREATED_BY_GROUP_DESC
}

input ArchiveFormInput {
  id: ID!
  clientMutationId: String
}

type ArchiveFormPayload {
  form: Form
  clientMutationId: String
}

input ArchiveQuestionInput {
  id: ID!
  clientMutationId: String
}

type ArchiveQuestionPayload {
  question: Question
  clientMutationId: String
}

input ArchiveTaskInput {
  id: ID!
  clientMutationId: String
}

type ArchiveTaskPayload {
  task: Task
  clientMutationId: String
}

input ArchiveWorkflowInput {
  id: ID!
  clientMutationId: String
}

type ArchiveWorkflowPayload {
  workflow: Workflow
  clientMutationId: String
}

input CancelCaseInput {
  id: ID!
  clientMutationId: String
}

type CancelCasePayload {
  case: Case
  clientMutationId: String
}

type Case implements Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  workflow: Workflow!
  status: CaseStatus!
  meta: JSONString!
  document: Document
  workItems(before: String, after: String, first: Int, last: Int): WorkItemConnection
}

type CaseConnection {
  pageInfo: PageInfo!
  edges: [CaseEdge]!
}

type CaseEdge {
  node: Case
  cursor: String!
}

enum CaseOrdering {
  STATUS_ASC
  STATUS_DESC
  CREATED_AT_ASC
  CREATED_AT_DESC
  MODIFIED_AT_ASC
  MODIFIED_AT_DESC
  CREATED_BY_USER_ASC
  CREATED_BY_USER_DESC
  CREATED_BY_GROUP_ASC
  CREATED_BY_GROUP_DESC
}

enum CaseStatus {
  RUNNING
  COMPLETED
  CANCELED
}

type CheckboxQuestion implements Question, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  slug: String!
  label: String!
  isRequired: QuestionJexl!
  isHidden: QuestionJexl!
  isArchived: Boolean!
  meta: JSONString!
  forms(before: String, after: String, first: Int, last: Int, orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, search: String): FormConnection
  options(before: String, after: String, first: Int, last: Int, orderBy: [OptionOrdering], slug: String, label: String, search: String): OptionConnection
  id: ID!
}

input CompleteWorkItemInput {
  id: ID!
  clientMutationId: String
}

type CompleteWorkItemPayload {
  workItem: WorkItem
  clientMutationId: String
}

scalar DateTime

type Document implements Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  form: Form!
  meta: JSONString!
  answers(before: String, after: String, first: Int, last: Int, question: ID, search: String, orderBy: [AnswerOrdering]): AnswerConnection
}

type DocumentConnection {
  pageInfo: PageInfo!
  edges: [DocumentEdge]!
}

type DocumentEdge {
  node: Document
  cursor: String!
}

enum DocumentOrdering {
  CREATED_AT_ASC
  CREATED_AT_DESC
  MODIFIED_AT_ASC
  MODIFIED_AT_DESC
  CREATED_BY_USER_ASC
  CREATED_BY_USER_DESC
  CREATED_BY_GROUP_ASC
  CREATED_BY_GROUP_DESC
}

type FloatAnswer implements Answer, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  question: Question!
  value: Float!
  meta: JSONString!
}

type FloatQuestion implements Question, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  slug: String!
  label: String!
  isRequired: QuestionJexl!
  isHidden: QuestionJexl!
  isArchived: Boolean!
  meta: JSONString!
  forms(before: String, after: String, first: Int, last: Int, orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, search: String): FormConnection
  id: ID!
  minValue: Float
  maxValue: Float
}

type Flow implements Node {
  task: Task!
  next: FlowJexl!
  id: ID!
}

type FlowConnection {
  pageInfo: PageInfo!
  edges: [FlowEdge]!
}

type FlowEdge {
  node: Flow
  cursor: String!
}

scalar FlowJexl

type Form implements Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  slug: String!
  name: String!
  description: String
  meta: JSONString!
  isPublished: Boolean!
  isArchived: Boolean!
  questions(before: String, after: String, first: Int, last: Int, slug: String, label: String, isRequired: String, isHidden: String, isArchived: Boolean, excludeForms: [ID], search: String, orderBy: [QuestionOrdering]): QuestionConnection
  id: ID!
}

type FormConnection {
  pageInfo: PageInfo!
  edges: [FormEdge]!
}

type FormEdge {
  node: Form
  cursor: String!
}

enum FormOrdering {
  NAME_ASC
  NAME_DESC
  CREATED_AT_ASC
  CREATED_AT_DESC
  MODIFIED_AT_ASC
  MODIFIED_AT_DESC
  CREATED_BY_USER_ASC
  CREATED_BY_USER_DESC
  CREATED_BY_GROUP_ASC
  CREATED_BY_GROUP_DESC
}

type IntegerAnswer implements Answer, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  question: Question!
  value: Int!
  meta: JSONString!
}

type IntegerQuestion implements Question, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  slug: String!
  label: String!
  isRequired: QuestionJexl!
  isHidden: QuestionJexl!
  isArchived: Boolean!
  meta: JSONString!
  forms(before: String, after: String, first: Int, last: Int, orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, search: String): FormConnection
  id: ID!
  maxValue: Int
  minValue: Int
}

scalar JSONString

type ListAnswer implements Answer, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  question: Question!
  value: [String]!
  meta: JSONString!
}

type Mutation {
  saveWorkflow(input: SaveWorkflowInput!): SaveWorkflowPayload
  publishWorkflow(input: PublishWorkflowInput!): PublishWorkflowPayload
  archiveWorkflow(input: ArchiveWorkflowInput!): ArchiveWorkflowPayload
  addWorkflowFlow(input: AddWorkflowFlowInput!): AddWorkflowFlowPayload
  removeWorkflowFlow(input: RemoveWorkflowFlowInput!): RemoveWorkflowFlowPayload
  saveTask(input: SaveTaskInput!): SaveTaskPayload
  archiveTask(input: ArchiveTaskInput!): ArchiveTaskPayload
  startCase(input: StartCaseInput!): StartCasePayload
  cancelCase(input: CancelCaseInput!): CancelCasePayload
  completeWorkItem(input: CompleteWorkItemInput!): CompleteWorkItemPayload
  saveForm(input: SaveFormInput!): SaveFormPayload
  archiveForm(input: ArchiveFormInput!): ArchiveFormPayload
  publishForm(input: PublishFormInput!): PublishFormPayload
  addFormQuestion(input: AddFormQuestionInput!): AddFormQuestionPayload
  removeFormQuestion(input: RemoveFormQuestionInput!): RemoveFormQuestionPayload
  reorderFormQuestions(input: ReorderFormQuestionsInput!): ReorderFormQuestionsPayload
  saveOption(input: SaveOptionInput!): SaveOptionPayload
  removeOption(input: RemoveOptionInput!): RemoveOptionPayload
  saveTextQuestion(input: SaveTextQuestionInput!): SaveTextQuestionPayload
  saveTextareaQuestion(input: SaveTextareaQuestionInput!): SaveTextareaQuestionPayload
  saveRadioQuestion(input: SaveRadioQuestionInput!): SaveRadioQuestionPayload
  saveCheckboxQuestion(input: SaveCheckboxQuestionInput!): SaveCheckboxQuestionPayload
  saveFloatQuestion(input: SaveFloatQuestionInput!): SaveFloatQuestionPayload
  saveIntegerQuestion(input: SaveIntegerQuestionInput!): SaveIntegerQuestionPayload
  archiveQuestion(input: ArchiveQuestionInput!): ArchiveQuestionPayload
  saveDocument(input: SaveDocumentInput!): SaveDocumentPayload
  saveDocumentStringAnswer(input: SaveDocumentStringAnswerInput!): SaveDocumentStringAnswerPayload
  saveDocumentIntegerAnswer(input: SaveDocumentIntegerAnswerInput!): SaveDocumentIntegerAnswerPayload
  saveDocumentFloatAnswer(input: SaveDocumentFloatAnswerInput!): SaveDocumentFloatAnswerPayload
  saveDocumentListAnswer(input: SaveDocumentListAnswerInput!): SaveDocumentListAnswerPayload
}

interface Node {
  id: ID!
}

type Option implements Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  slug: String!
  label: String!
  meta: JSONString!
  id: ID!
}

type OptionConnection {
  pageInfo: PageInfo!
  edges: [OptionEdge]!
}

type OptionEdge {
  node: Option
  cursor: String!
}

enum OptionOrdering {
  LABEL_ASC
  LABEL_DESC
  CREATED_AT_ASC
  CREATED_AT_DESC
  MODIFIED_AT_ASC
  MODIFIED_AT_DESC
  CREATED_BY_USER_ASC
  CREATED_BY_USER_DESC
  CREATED_BY_GROUP_ASC
  CREATED_BY_GROUP_DESC
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

input PublishFormInput {
  id: ID!
  clientMutationId: String
}

type PublishFormPayload {
  form: Form
  clientMutationId: String
}

input PublishWorkflowInput {
  id: ID!
  clientMutationId: String
}

type PublishWorkflowPayload {
  workflow: Workflow
  clientMutationId: String
}

type Query {
  allWorkflows(before: String, after: String, first: Int, last: Int, slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, search: String, orderBy: [WorkflowOrdering]): WorkflowConnection
  allTasks(before: String, after: String, first: Int, last: Int, slug: String, name: String, description: String, type: String, isArchived: Boolean, search: String, orderBy: [TaskOrdering]): TaskConnection
  allCases(before: String, after: String, first: Int, last: Int, workflow: ID, status: String, orderBy: [CaseOrdering]): CaseConnection
  allWorkItems(before: String, after: String, first: Int, last: Int, status: String, task: ID, case: ID, orderBy: [WorkItemOrdering]): WorkItemConnection
  allForms(before: String, after: String, first: Int, last: Int, orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, search: String): FormConnection
  allQuestions(before: String, after: String, first: Int, last: Int, orderBy: [QuestionOrdering], slug: String, label: String, isRequired: String, isHidden: String, isArchived: Boolean, excludeForms: [ID], search: String): QuestionConnection
  allDocuments(before: String, after: String, first: Int, last: Int, form: ID, search: String, id: ID, orderBy: [DocumentOrdering]): DocumentConnection
  node(id: ID!): Node
}

interface Question {
  id: ID!
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  slug: String!
  label: String!
  isRequired: QuestionJexl!
  isHidden: QuestionJexl!
  isArchived: Boolean!
  meta: JSONString!
  forms(before: String, after: String, first: Int, last: Int, slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, search: String, orderBy: [FormOrdering]): FormConnection
}

type QuestionConnection {
  pageInfo: PageInfo!
  edges: [QuestionEdge]!
}

type QuestionEdge {
  node: Question
  cursor: String!
}

scalar QuestionJexl

enum QuestionOrdering {
  LABEL_ASC
  LABEL_DESC
  CREATED_AT_ASC
  CREATED_AT_DESC
  MODIFIED_AT_ASC
  MODIFIED_AT_DESC
  CREATED_BY_USER_ASC
  CREATED_BY_USER_DESC
  CREATED_BY_GROUP_ASC
  CREATED_BY_GROUP_DESC
}

type RadioQuestion implements Question, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  slug: String!
  label: String!
  isRequired: QuestionJexl!
  isHidden: QuestionJexl!
  isArchived: Boolean!
  meta: JSONString!
  forms(before: String, after: String, first: Int, last: Int, orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, search: String): FormConnection
  options(before: String, after: String, first: Int, last: Int, slug: String, label: String, search: String, orderBy: [OptionOrdering]): OptionConnection
  id: ID!
}

input RemoveFormQuestionInput {
  form: ID!
  question: ID!
  clientMutationId: String
}

type RemoveFormQuestionPayload {
  form: Form
  clientMutationId: String
}

input RemoveOptionInput {
  option: ID!
  clientMutationId: String
}

type RemoveOptionPayload {
  clientMutationId: String
}

input RemoveWorkflowFlowInput {
  workflow: ID!
  task: ID!
  clientMutationId: String
}

type RemoveWorkflowFlowPayload {
  workflow: Workflow
  clientMutationId: String
}

input ReorderFormQuestionsInput {
  form: ID!
  questions: [ID]!
  clientMutationId: String
}

type ReorderFormQuestionsPayload {
  form: Form
  clientMutationId: String
}

input SaveCheckboxQuestionInput {
  slug: String!
  label: String!
  isRequired: QuestionJexl
  isHidden: QuestionJexl
  meta: JSONString
  options: [ID]!
  clientMutationId: String
}

type SaveCheckboxQuestionPayload {
  question: Question
  clientMutationId: String
}

input SaveDocumentFloatAnswerInput {
  question: ID!
  document: ID!
  value: Float!
  meta: JSONString
  clientMutationId: String
}

type SaveDocumentFloatAnswerPayload {
  answer: Answer
  clientMutationId: String
}

input SaveDocumentInput {
  form: ID!
  meta: JSONString
  clientMutationId: String
}

input SaveDocumentIntegerAnswerInput {
  question: ID!
  document: ID!
  value: Int!
  meta: JSONString
  clientMutationId: String
}

type SaveDocumentIntegerAnswerPayload {
  answer: Answer
  clientMutationId: String
}

input SaveDocumentListAnswerInput {
  question: ID!
  document: ID!
  value: [String]!
  meta: JSONString
  clientMutationId: String
}

type SaveDocumentListAnswerPayload {
  answer: Answer
  clientMutationId: String
}

type SaveDocumentPayload {
  document: Document
  clientMutationId: String
}

input SaveDocumentStringAnswerInput {
  question: ID!
  document: ID!
  value: String!
  meta: JSONString
  clientMutationId: String
}

type SaveDocumentStringAnswerPayload {
  answer: Answer
  clientMutationId: String
}

input SaveFloatQuestionInput {
  slug: String!
  label: String!
  isRequired: QuestionJexl
  isHidden: QuestionJexl
  meta: JSONString
  minValue: Float
  maxValue: Float
  clientMutationId: String
}

type SaveFloatQuestionPayload {
  question: Question
  clientMutationId: String
}

input SaveFormInput {
  slug: String!
  name: String!
  description: String
  meta: JSONString
  clientMutationId: String
}

type SaveFormPayload {
  form: Form
  clientMutationId: String
}

input SaveIntegerQuestionInput {
  slug: String!
  label: String!
  isRequired: QuestionJexl
  isHidden: QuestionJexl
  meta: JSONString
  minValue: Int
  maxValue: Int
  clientMutationId: String
}

type SaveIntegerQuestionPayload {
  question: Question
  clientMutationId: String
}

input SaveOptionInput {
  slug: String!
  label: String!
  meta: JSONString
  clientMutationId: String
}

type SaveOptionPayload {
  option: Option
  clientMutationId: String
}

input SaveRadioQuestionInput {
  slug: String!
  label: String!
  isRequired: QuestionJexl
  isHidden: QuestionJexl
  meta: JSONString
  options: [ID]!
  clientMutationId: String
}

type SaveRadioQuestionPayload {
  question: Question
  clientMutationId: String
}

input SaveTaskInput {
  slug: String!
  name: String!
  description: String
  type: TaskType!
  clientMutationId: String
}

type SaveTaskPayload {
  task: Task
  clientMutationId: String
}

input SaveTextQuestionInput {
  slug: String!
  label: String!
  isRequired: QuestionJexl
  isHidden: QuestionJexl
  meta: JSONString
  maxLength: Int
  clientMutationId: String
}

type SaveTextQuestionPayload {
  question: Question
  clientMutationId: String
}

input SaveTextareaQuestionInput {
  slug: String!
  label: String!
  isRequired: QuestionJexl
  isHidden: QuestionJexl
  meta: JSONString
  maxLength: Int
  clientMutationId: String
}

type SaveTextareaQuestionPayload {
  question: Question
  clientMutationId: String
}

input SaveWorkflowInput {
  slug: String!
  name: String!
  description: String
  meta: JSONString
  start: ID!
  form: ID
  clientMutationId: String
}

type SaveWorkflowPayload {
  workflow: Workflow
  clientMutationId: String
}

input StartCaseInput {
  workflow: ID!
  meta: JSONString
  clientMutationId: String
}

type StartCasePayload {
  case: Case
  clientMutationId: String
}

type StringAnswer implements Answer, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  question: Question!
  value: String!
  meta: JSONString!
}

type Task implements Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  slug: String!
  name: String!
  description: String
  type: TaskType!
  meta: JSONString!
  isArchived: Boolean!
  id: ID!
}

type TaskConnection {
  pageInfo: PageInfo!
  edges: [TaskEdge]!
}

type TaskEdge {
  node: Task
  cursor: String!
}

enum TaskOrdering {
  NAME_ASC
  NAME_DESC
  DESCRIPTION_ASC
  DESCRIPTION_DESC
  TYPE_ASC
  TYPE_DESC
  CREATED_AT_ASC
  CREATED_AT_DESC
  MODIFIED_AT_ASC
  MODIFIED_AT_DESC
  CREATED_BY_USER_ASC
  CREATED_BY_USER_DESC
  CREATED_BY_GROUP_ASC
  CREATED_BY_GROUP_DESC
}

enum TaskType {
  SIMPLE
}

type TextQuestion implements Question, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  slug: String!
  label: String!
  isRequired: QuestionJexl!
  isHidden: QuestionJexl!
  isArchived: Boolean!
  meta: JSONString!
  forms(before: String, after: String, first: Int, last: Int, orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, search: String): FormConnection
  id: ID!
  maxLength: Int
}

type TextareaQuestion implements Question, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  slug: String!
  label: String!
  isRequired: QuestionJexl!
  isHidden: QuestionJexl!
  isArchived: Boolean!
  meta: JSONString!
  forms(before: String, after: String, first: Int, last: Int, orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, search: String): FormConnection
  id: ID!
  maxLength: Int
}

type WorkItem implements Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  task: Task!
  case: Case!
  status: WorkItemStatus!
  meta: JSONString!
}

type WorkItemConnection {
  pageInfo: PageInfo!
  edges: [WorkItemEdge]!
}

type WorkItemEdge {
  node: WorkItem
  cursor: String!
}

enum WorkItemOrdering {
  STATUS_ASC
  STATUS_DESC
  CREATED_AT_ASC
  CREATED_AT_DESC
  MODIFIED_AT_ASC
  MODIFIED_AT_DESC
  CREATED_BY_USER_ASC
  CREATED_BY_USER_DESC
  CREATED_BY_GROUP_ASC
  CREATED_BY_GROUP_DESC
}

enum WorkItemStatus {
  READY
  COMPLETED
  CANCELED
}

type Workflow implements Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  slug: String!
  name: String!
  description: String
  meta: JSONString!
  isPublished: Boolean!
  isArchived: Boolean!
  start: Task!
  form: Form
  flows(before: String, after: String, first: Int, last: Int, task: ID): FlowConnection
  id: ID!
}

type WorkflowConnection {
  pageInfo: PageInfo!
  edges: [WorkflowEdge]!
}

type WorkflowEdge {
  node: Workflow
  cursor: String!
}

enum WorkflowOrdering {
  NAME_ASC
  NAME_DESC
  DESCRIPTION_ASC
  DESCRIPTION_DESC
  CREATED_AT_ASC
  CREATED_AT_DESC
  MODIFIED_AT_ASC
  MODIFIED_AT_DESC
  CREATED_BY_USER_ASC
  CREATED_BY_USER_DESC
  CREATED_BY_GROUP_ASC
  CREATED_BY_GROUP_DESC
}
"""
