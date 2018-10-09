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

input AddWorkflowSpecificationFlowInput {
  workflowSpecification: ID!
  task: ID!
  next: FlowJexl!
  clientMutationId: String
}

type AddWorkflowSpecificationFlowPayload {
  workflowSpecification: WorkflowSpecification
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

input ArchiveWorkflowSpecificationInput {
  id: ID!
  clientMutationId: String
}

type ArchiveWorkflowSpecificationPayload {
  workflowSpecification: WorkflowSpecification
  clientMutationId: String
}

type CheckboxQuestion implements Question, Node {
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
  options(before: String, after: String, first: Int, last: Int, slug: String, label: String, search: String): OptionConnection
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
  answers(before: String, after: String, first: Int, last: Int): AnswerConnection
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
  id: ID!
  created: DateTime!
  modified: DateTime!
  question: Question!
  meta: JSONString
  value: Float!
}

type FloatQuestion implements Question, Node {
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
  id: ID!
  questions(before: String, after: String, first: Int, last: Int, slug: String, label: String, isRequired: String, isHidden: String, isArchived: Boolean, excludeForms: [ID], search: String): QuestionConnection
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
  id: ID!
  created: DateTime!
  modified: DateTime!
  question: Question!
  meta: JSONString
  value: Int!
}

type IntegerQuestion implements Question, Node {
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
  maxValue: Int
  minValue: Int
}

scalar JSONString

type ListAnswer implements Answer, Node {
  id: ID!
  created: DateTime!
  modified: DateTime!
  question: Question!
  meta: JSONString
  value: [String]!
}

type Mutation {
  saveWorkflowSpecification(input: SaveWorkflowSpecificationInput!): SaveWorkflowSpecificationPayload
  publishWorkflowSpecification(input: PublishWorkflowSpecificationInput!): PublishWorkflowSpecificationPayload
  archiveWorkflowSpecification(input: ArchiveWorkflowSpecificationInput!): ArchiveWorkflowSpecificationPayload
  addWorkflowSpecificationFlow(input: AddWorkflowSpecificationFlowInput!): AddWorkflowSpecificationFlowPayload
  removeWorkflowSpecificationFlow(input: RemoveWorkflowSpecificationFlowInput!): RemoveWorkflowSpecificationFlowPayload
  saveTask(input: SaveTaskInput!): SaveTaskPayload
  archiveTask(input: ArchiveTaskInput!): ArchiveTaskPayload
  startWorkflow(input: StartWorkflowInput!): StartWorkflowPayload
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

input PublishWorkflowSpecificationInput {
  id: ID!
  clientMutationId: String
}

type PublishWorkflowSpecificationPayload {
  workflowSpecification: WorkflowSpecification
  clientMutationId: String
}

type Query {
  allWorkflowSpecifications(before: String, after: String, first: Int, last: Int, slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, search: String): WorkflowSpecificationConnection
  allTasks(before: String, after: String, first: Int, last: Int, slug: String, name: String, description: String, type: String, isArchived: Boolean, search: String): TaskConnection
  allWorkflows(before: String, after: String, first: Int, last: Int, workflowSpecification: ID, status: String): WorkflowConnection
  allWorkItems(before: String, after: String, first: Int, last: Int, status: String, task: ID, workflow: ID): WorkItemConnection
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
  options(before: String, after: String, first: Int, last: Int, slug: String, label: String, search: String): OptionConnection
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

input RemoveWorkflowSpecificationFlowInput {
  workflowSpecification: ID!
  task: ID!
  clientMutationId: String
}

type RemoveWorkflowSpecificationFlowPayload {
  workflowSpecification: WorkflowSpecification
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

input SaveWorkflowSpecificationInput {
  slug: String!
  name: String!
  description: String
  meta: JSONString
  start: ID!
  clientMutationId: String
}

type SaveWorkflowSpecificationPayload {
  workflowSpecification: WorkflowSpecification
  clientMutationId: String
}

input StartWorkflowInput {
  workflowSpecification: ID!
  meta: JSONString
  clientMutationId: String
}

type StartWorkflowPayload {
  workflow: Workflow
  clientMutationId: String
}

type StringAnswer implements Answer, Node {
  id: ID!
  created: DateTime!
  modified: DateTime!
  question: Question!
  meta: JSONString
  value: String!
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
  maxLength: Int
}

type TextareaQuestion implements Question, Node {
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
  maxLength: Int
}

type WorkItem implements Node {
  created: DateTime!
  modified: DateTime!
  id: ID!
  task: Task!
  workflow: Workflow!
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
  id: ID!
  workflowSpecification: WorkflowSpecification!
  status: WorkflowStatus!
  meta: JSONString!
  workItems(before: String, after: String, first: Int, last: Int): WorkItemConnection
}

type WorkflowConnection {
  pageInfo: PageInfo!
  edges: [WorkflowEdge]!
}

type WorkflowEdge {
  node: Workflow
  cursor: String!
}

type WorkflowSpecification implements Node {
  created: DateTime!
  modified: DateTime!
  slug: String!
  name: String!
  description: String
  meta: JSONString!
  isPublished: Boolean!
  isArchived: Boolean!
  start: Task!
  id: ID!
  flows(before: String, after: String, first: Int, last: Int, task: ID): FlowConnection
}

type WorkflowSpecificationConnection {
  pageInfo: PageInfo!
  edges: [WorkflowSpecificationEdge]!
}

type WorkflowSpecificationEdge {
  node: WorkflowSpecification
  cursor: String!
}

enum WorkflowStatus {
  RUNNING
  COMPLETE
}
"""
