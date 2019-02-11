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
  tasks: [ID]!
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
  workItems(before: String, after: String, first: Int, last: Int, status: WorkItemStatusArgument, task: ID, case: ID, orderBy: [WorkItemOrdering]): WorkItemConnection
  parentWorkItem: WorkItem
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

enum CaseStatusArgument {
  RUNNING
  COMPLETED
  CANCELED
}

type ChoiceQuestion implements Question, Node {
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
  source: Question
  forms(before: String, after: String, first: Int, last: Int, orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, search: String): FormConnection
  options(before: String, after: String, first: Int, last: Int, slug: String, label: String, search: String, orderBy: [OptionOrdering]): OptionConnection
  id: ID!
}

type CompleteTaskFormTask implements Task, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  slug: String!
  name: String!
  description: String
  type: TaskType!
  meta: JSONString!
  addressGroups: GroupJexl
  isArchived: Boolean!
  form: Form!
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

type CompleteWorkflowFormTask implements Task, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  slug: String!
  name: String!
  description: String
  type: TaskType!
  meta: JSONString!
  addressGroups: GroupJexl
  isArchived: Boolean!
  id: ID!
}

input CopyFormInput {
  slug: String!
  name: String!
  description: String
  source: ID!
  clientMutationId: String
}

type CopyFormPayload {
  form: Form
  clientMutationId: String
}

input CopyOptionInput {
  slug: String!
  label: String!
  source: ID!
  clientMutationId: String
}

type CopyOptionPayload {
  option: Option
  clientMutationId: String
}

input CopyQuestionInput {
  slug: String!
  label: String!
  source: ID!
  clientMutationId: String
}

type CopyQuestionPayload {
  question: Question
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
  case: Case
  workItem: WorkItem
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
  source: Question
  forms(before: String, after: String, first: Int, last: Int, orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, search: String): FormConnection
  id: ID!
  minValue: Float
  maxValue: Float
}

type Flow implements Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  next: FlowJexl!
  tasks: [Task]!
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
  source: Form
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

scalar GroupJexl

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
  source: Question
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

type MultipleChoiceQuestion implements Question, Node {
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
  source: Question
  forms(before: String, after: String, first: Int, last: Int, orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, search: String): FormConnection
  options(before: String, after: String, first: Int, last: Int, orderBy: [OptionOrdering], slug: String, label: String, search: String): OptionConnection
  id: ID!
}

type Mutation {
  saveWorkflow(input: SaveWorkflowInput!): SaveWorkflowPayload
  addWorkflowFlow(input: AddWorkflowFlowInput!): AddWorkflowFlowPayload
  removeFlow(input: RemoveFlowInput!): RemoveFlowPayload
  saveSimpleTask(input: SaveSimpleTaskInput!): SaveSimpleTaskPayload
  saveCompleteWorkflowFormTask(input: SaveCompleteWorkflowFormTaskInput!): SaveCompleteWorkflowFormTaskPayload
  saveCompleteTaskFormTask(input: SaveCompleteTaskFormTaskInput!): SaveCompleteTaskFormTaskPayload
  startCase(input: StartCaseInput!): StartCasePayload
  cancelCase(input: CancelCaseInput!): CancelCasePayload
  completeWorkItem(input: CompleteWorkItemInput!): CompleteWorkItemPayload
  saveWorkItem(input: SaveWorkItemInput!): SaveWorkItemPayload
  saveForm(input: SaveFormInput!): SaveFormPayload
  copyForm(input: CopyFormInput!): CopyFormPayload
  addFormQuestion(input: AddFormQuestionInput!): AddFormQuestionPayload
  removeFormQuestion(input: RemoveFormQuestionInput!): RemoveFormQuestionPayload
  reorderFormQuestions(input: ReorderFormQuestionsInput!): ReorderFormQuestionsPayload
  saveOption(input: SaveOptionInput!): SaveOptionPayload
  removeOption(input: RemoveOptionInput!): RemoveOptionPayload
  copyOption(input: CopyOptionInput!): CopyOptionPayload
  copyQuestion(input: CopyQuestionInput!): CopyQuestionPayload
  saveTextQuestion(input: SaveTextQuestionInput!): SaveTextQuestionPayload
  saveTextareaQuestion(input: SaveTextareaQuestionInput!): SaveTextareaQuestionPayload
  saveChoiceQuestion(input: SaveChoiceQuestionInput!): SaveChoiceQuestionPayload
  saveMultipleChoiceQuestion(input: SaveMultipleChoiceQuestionInput!): SaveMultipleChoiceQuestionPayload
  saveFloatQuestion(input: SaveFloatQuestionInput!): SaveFloatQuestionPayload
  saveIntegerQuestion(input: SaveIntegerQuestionInput!): SaveIntegerQuestionPayload
  saveTableQuestion(input: SaveTableQuestionInput!): SaveTableQuestionPayload
  saveDocument(input: SaveDocumentInput!): SaveDocumentPayload
  saveDocumentStringAnswer(input: SaveDocumentStringAnswerInput!): SaveDocumentStringAnswerPayload
  saveDocumentIntegerAnswer(input: SaveDocumentIntegerAnswerInput!): SaveDocumentIntegerAnswerPayload
  saveDocumentFloatAnswer(input: SaveDocumentFloatAnswerInput!): SaveDocumentFloatAnswerPayload
  saveDocumentListAnswer(input: SaveDocumentListAnswerInput!): SaveDocumentListAnswerPayload
  saveDocumentTableAnswer(input: SaveDocumentTableAnswerInput!): SaveDocumentTableAnswerPayload
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
  source: Option
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

type Query {
  allWorkflows(before: String, after: String, first: Int, last: Int, slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, search: String, orderBy: [WorkflowOrdering]): WorkflowConnection
  allTasks(before: String, after: String, first: Int, last: Int, slug: String, name: String, description: String, type: TaskTypeArgument, isArchived: Boolean, search: String, orderBy: [TaskOrdering]): TaskConnection
  allCases(before: String, after: String, first: Int, last: Int, workflow: ID, status: CaseStatusArgument, orderBy: [CaseOrdering]): CaseConnection
  allWorkItems(before: String, after: String, first: Int, last: Int, status: WorkItemStatusArgument, orderBy: [WorkItemOrdering], task: ID, case: ID): WorkItemConnection
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
  source: Question
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

input RemoveFlowInput {
  flow: ID!
  clientMutationId: String
}

type RemoveFlowPayload {
  flow: Flow
  clientMutationId: String
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

input ReorderFormQuestionsInput {
  form: ID!
  questions: [ID]!
  clientMutationId: String
}

type ReorderFormQuestionsPayload {
  form: Form
  clientMutationId: String
}

input SaveChoiceQuestionInput {
  slug: String!
  label: String!
  isRequired: QuestionJexl
  isHidden: QuestionJexl
  meta: JSONString
  isArchived: Boolean
  options: [ID]!
  clientMutationId: String
}

type SaveChoiceQuestionPayload {
  question: Question
  clientMutationId: String
}

input SaveCompleteTaskFormTaskInput {
  slug: String!
  name: String!
  description: String
  meta: JSONString
  addressGroups: GroupJexl
  isArchived: Boolean
  form: ID!
  clientMutationId: String
}

type SaveCompleteTaskFormTaskPayload {
  task: Task
  clientMutationId: String
}

input SaveCompleteWorkflowFormTaskInput {
  slug: String!
  name: String!
  description: String
  meta: JSONString
  addressGroups: GroupJexl
  isArchived: Boolean
  clientMutationId: String
}

type SaveCompleteWorkflowFormTaskPayload {
  task: Task
  clientMutationId: String
}

input SaveDocumentFloatAnswerInput {
  question: ID!
  document: ID!
  meta: JSONString
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
  meta: JSONString
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
  meta: JSONString
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
  meta: JSONString
  value: String!
  clientMutationId: String
}

type SaveDocumentStringAnswerPayload {
  answer: Answer
  clientMutationId: String
}

input SaveDocumentTableAnswerInput {
  question: ID!
  document: ID!
  meta: JSONString
  value: [ID]!
  clientMutationId: String
}

type SaveDocumentTableAnswerPayload {
  answer: Answer
  clientMutationId: String
}

input SaveFloatQuestionInput {
  slug: String!
  label: String!
  isRequired: QuestionJexl
  isHidden: QuestionJexl
  meta: JSONString
  isArchived: Boolean
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
  isArchived: Boolean
  isPublished: Boolean
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
  isArchived: Boolean
  minValue: Int
  maxValue: Int
  clientMutationId: String
}

type SaveIntegerQuestionPayload {
  question: Question
  clientMutationId: String
}

input SaveMultipleChoiceQuestionInput {
  slug: String!
  label: String!
  isRequired: QuestionJexl
  isHidden: QuestionJexl
  meta: JSONString
  isArchived: Boolean
  options: [ID]!
  clientMutationId: String
}

type SaveMultipleChoiceQuestionPayload {
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

input SaveSimpleTaskInput {
  slug: String!
  name: String!
  description: String
  meta: JSONString
  addressGroups: GroupJexl
  isArchived: Boolean
  clientMutationId: String
}

type SaveSimpleTaskPayload {
  task: Task
  clientMutationId: String
}

input SaveTableQuestionInput {
  slug: String!
  label: String!
  isRequired: QuestionJexl
  isHidden: QuestionJexl
  meta: JSONString
  isArchived: Boolean
  rowForm: ID!
  clientMutationId: String
}

type SaveTableQuestionPayload {
  question: Question
  clientMutationId: String
}

input SaveTextQuestionInput {
  slug: String!
  label: String!
  isRequired: QuestionJexl
  isHidden: QuestionJexl
  meta: JSONString
  isArchived: Boolean
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
  isArchived: Boolean
  maxLength: Int
  clientMutationId: String
}

type SaveTextareaQuestionPayload {
  question: Question
  clientMutationId: String
}

input SaveWorkItemInput {
  workItem: ID!
  assignedUsers: [String]
  meta: JSONString
  clientMutationId: String
}

type SaveWorkItemPayload {
  workItem: WorkItem
  clientMutationId: String
}

input SaveWorkflowInput {
  slug: String!
  name: String!
  description: String
  meta: JSONString
  startTasks: [ID]!
  allowAllForms: Boolean
  allowForms: [ID]
  isArchived: Boolean
  isPublished: Boolean
  clientMutationId: String
}

type SaveWorkflowPayload {
  workflow: Workflow
  clientMutationId: String
}

type SimpleTask implements Task, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  slug: String!
  name: String!
  description: String
  type: TaskType!
  meta: JSONString!
  addressGroups: GroupJexl
  isArchived: Boolean!
  id: ID!
}

input StartCaseInput {
  workflow: ID!
  meta: JSONString
  parentWorkItem: ID
  form: ID
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

type TableAnswer implements Answer, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  question: Question!
  value: [Document]!
  meta: JSONString!
  document: Document!
}

type TableQuestion implements Question, Node {
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
  source: Question
  forms(before: String, after: String, first: Int, last: Int, orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, search: String): FormConnection
  rowForm: Form
  id: ID!
}

interface Task {
  id: ID!
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  slug: String!
  name: String!
  description: String
  isArchived: Boolean!
  addressGroups: GroupJexl
  meta: JSONString!
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
  COMPLETE_WORKFLOW_FORM
  COMPLETE_TASK_FORM
}

enum TaskTypeArgument {
  SIMPLE
  COMPLETE_WORKFLOW_FORM
  COMPLETE_TASK_FORM
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
  source: Question
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
  source: Question
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
  status: WorkItemStatus!
  meta: JSONString!
  addressedGroups: [String]!
  assignedUsers: [String]!
  case: Case!
  childCase: Case
  document: Document
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

enum WorkItemStatusArgument {
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
  startTasks: [Task]!
  allowAllForms: Boolean!
  allowForms(before: String, after: String, first: Int, last: Int): FormConnection
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
