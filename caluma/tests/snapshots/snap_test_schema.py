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
  created: DateTime!
  modified: DateTime!
  question: Question!
  meta: JSONString
}

type AnswerConnection {
  pageInfo: PageInfo!
  edges: [AnswerEdge]!
}

type AnswerEdge {
  node: Answer
  cursor: String!
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

type Case implements Node {
  created: DateTime!
  modified: DateTime!
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

enum CaseStatus {
  RUNNING
  COMPLETE
}

type CheckboxQuestion implements Question, Node {
  created: DateTime!
  modified: DateTime!
  slug: String!
  label: String!
  isRequired: QuestionJexl!
  isHidden: QuestionJexl!
  isArchived: Boolean!
  meta: JSONString
  forms(before: String, after: String, first: Int, last: Int, slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, search: String): FormConnection
  options(before: String, after: String, first: Int, last: Int, slug: String, label: String, search: String): OptionConnection
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
  created: DateTime!
  modified: DateTime!
  form: Form!
  meta: JSONString!
  answers(before: String, after: String, first: Int, last: Int, question: ID, search: String): AnswerConnection
  id: ID!
}

type DocumentConnection {
  pageInfo: PageInfo!
  edges: [DocumentEdge]!
}

type DocumentEdge {
  node: Document
  cursor: String!
}

type FloatAnswer implements Answer, Node {
  created: DateTime!
  modified: DateTime!
  id: ID!
  question: Question!
  value: Float!
  meta: JSONString
}

type FloatQuestion implements Question, Node {
  created: DateTime!
  modified: DateTime!
  slug: String!
  label: String!
  isRequired: QuestionJexl!
  isHidden: QuestionJexl!
  isArchived: Boolean!
  meta: JSONString
  forms(before: String, after: String, first: Int, last: Int, slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, search: String): FormConnection
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
  created: DateTime!
  modified: DateTime!
  slug: String!
  name: String!
  description: String
  meta: JSONString!
  isPublished: Boolean!
  isArchived: Boolean!
  questions(before: String, after: String, first: Int, last: Int, slug: String, label: String, isRequired: String, isHidden: String, isArchived: Boolean, excludeForms: [ID], search: String): QuestionConnection
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

type IntegerAnswer implements Answer, Node {
  created: DateTime!
  modified: DateTime!
  id: ID!
  question: Question!
  value: Int!
  meta: JSONString
}

type IntegerQuestion implements Question, Node {
  created: DateTime!
  modified: DateTime!
  slug: String!
  label: String!
  isRequired: QuestionJexl!
  isHidden: QuestionJexl!
  isArchived: Boolean!
  meta: JSONString
  forms(before: String, after: String, first: Int, last: Int, slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, search: String): FormConnection
  id: ID!
  maxValue: Int
  minValue: Int
}

scalar JSONString

type ListAnswer implements Answer, Node {
  created: DateTime!
  modified: DateTime!
  id: ID!
  question: Question!
  value: [String]!
  meta: JSONString
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
  created: DateTime!
  modified: DateTime!
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
  allWorkflows(before: String, after: String, first: Int, last: Int, slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, search: String): WorkflowConnection
  allTasks(before: String, after: String, first: Int, last: Int, slug: String, name: String, description: String, type: String, isArchived: Boolean, search: String): TaskConnection
  allCases(before: String, after: String, first: Int, last: Int, workflow: ID, status: String): CaseConnection
  allWorkItems(before: String, after: String, first: Int, last: Int, status: String, task: ID, case: ID): WorkItemConnection
  allForms(before: String, after: String, first: Int, last: Int, slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, search: String): FormConnection
  allQuestions(before: String, after: String, first: Int, last: Int, slug: String, label: String, isRequired: String, isHidden: String, isArchived: Boolean, excludeForms: [ID], search: String): QuestionConnection
  allDocuments(before: String, after: String, first: Int, last: Int, form: ID, search: String): DocumentConnection
  node(id: ID!): Node
}

interface Question {
  id: ID!
  created: DateTime!
  modified: DateTime!
  slug: String!
  label: String!
  isRequired: QuestionJexl!
  isHidden: QuestionJexl!
  isArchived: Boolean!
  meta: JSONString
  forms(before: String, after: String, first: Int, last: Int, slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, search: String): FormConnection
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

type RadioQuestion implements Question, Node {
  created: DateTime!
  modified: DateTime!
  slug: String!
  label: String!
  isRequired: QuestionJexl!
  isHidden: QuestionJexl!
  isArchived: Boolean!
  meta: JSONString
  forms(before: String, after: String, first: Int, last: Int, slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, search: String): FormConnection
  options(before: String, after: String, first: Int, last: Int, slug: String, label: String, search: String): OptionConnection
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
  option: ID
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
  meta: JSONString!
  value: Float!
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
  meta: JSONString!
  value: Int!
  clientMutationId: String
}

type SaveDocumentIntegerAnswerPayload {
  answer: Answer
  clientMutationId: String
}

input SaveDocumentListAnswerInput {
  question: ID!
  document: ID!
  meta: JSONString!
  value: [String]!
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
  meta: JSONString!
  value: String!
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
  created: DateTime!
  modified: DateTime!
  id: ID!
  question: Question!
  value: String!
  meta: JSONString
}

type Task implements Node {
  created: DateTime!
  modified: DateTime!
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

enum TaskType {
  SIMPLE
}

type TextQuestion implements Question, Node {
  created: DateTime!
  modified: DateTime!
  slug: String!
  label: String!
  isRequired: QuestionJexl!
  isHidden: QuestionJexl!
  isArchived: Boolean!
  meta: JSONString
  forms(before: String, after: String, first: Int, last: Int, slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, search: String): FormConnection
  id: ID!
  maxLength: Int
}

type TextareaQuestion implements Question, Node {
  created: DateTime!
  modified: DateTime!
  slug: String!
  label: String!
  isRequired: QuestionJexl!
  isHidden: QuestionJexl!
  isArchived: Boolean!
  meta: JSONString
  forms(before: String, after: String, first: Int, last: Int, slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, search: String): FormConnection
  id: ID!
  maxLength: Int
}

type WorkItem implements Node {
  created: DateTime!
  modified: DateTime!
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

enum WorkItemStatus {
  READY
  COMPLETE
}

type Workflow implements Node {
  created: DateTime!
  modified: DateTime!
  slug: String!
  name: String!
  description: String
  meta: JSONString!
  isPublished: Boolean!
  isArchived: Boolean!
  start: Task!
  form: Form
  id: ID!
  flows(before: String, after: String, first: Int, last: Int, task: ID): FlowConnection
}

type WorkflowConnection {
  pageInfo: PageInfo!
  edges: [WorkflowEdge]!
}

type WorkflowEdge {
  node: Workflow
  cursor: String!
}
"""
