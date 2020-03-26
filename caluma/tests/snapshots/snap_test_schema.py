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
  meta: GenericScalar!
}

type AnswerConnection {
  pageInfo: PageInfo!
  edges: [AnswerEdge]!
  totalCount: Int
}

type AnswerEdge {
  node: Answer
  cursor: String!
}

input AnswerFilterSetType {
  question: ID
  search: String
  createdByUser: String
  createdByGroup: String
  metaHasKey: String
  metaValue: [JSONValueFilterType]
  orderBy: [AnswerOrdering]
  questions: [ID]
  visibleInContext: Boolean
  invert: Boolean
}

enum AnswerHierarchyMode {
  DIRECT
  FAMILY
}

enum AnswerLookupMode {
  EXACT
  STARTSWITH
  CONTAINS
  ICONTAINS
  INTERSECTS
  ISNULL
  GTE
  GT
  LTE
  LT
}

input AnswerOrderSetType {
  meta: String
  attribute: SortableAnswerAttributes
  direction: AscDesc
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
  META_TEST_KEY_ASC
  META_TEST_KEY_DESC
  META_FOOBAR_ASC
  META_FOOBAR_DESC
}

enum AscDesc {
  ASC
  DESC
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
  closedAt: DateTime
  closedByUser: String
  closedByGroup: String
  workflow: Workflow!
  status: CaseStatus!
  meta: GenericScalar
  document: Document
  workItems(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], status: WorkItemStatusArgument, name: String, task: ID, case: ID, createdAt: DateTime, closedAt: DateTime, modifiedAt: DateTime, orderBy: [WorkItemOrdering], filter: [WorkItemFilterSetType], order: [WorkItemOrderSetType], createdByUser: String, createdByGroup: String, metaHasKey: String, addressedGroups: [String], controllingGroups: [String], assignedUsers: [String], documentHasAnswer: [HasAnswerFilterType], caseDocumentHasAnswer: [HasAnswerFilterType], caseMetaValue: [JSONValueFilterType]): WorkItemConnection
  parentWorkItem: WorkItem
  familyWorkItems(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], status: WorkItemStatusArgument, orderBy: [WorkItemOrdering], filter: [WorkItemFilterSetType], order: [WorkItemOrderSetType], documentHasAnswer: [HasAnswerFilterType], caseDocumentHasAnswer: [HasAnswerFilterType], caseMetaValue: [JSONValueFilterType], name: String, task: ID, case: ID, createdAt: DateTime, closedAt: DateTime, modifiedAt: DateTime, createdByUser: String, createdByGroup: String, metaHasKey: String, addressedGroups: [String], controllingGroups: [String], assignedUsers: [String]): WorkItemConnection
}

type CaseConnection {
  pageInfo: PageInfo!
  edges: [CaseEdge]!
  totalCount: Int
}

type CaseEdge {
  node: Case
  cursor: String!
}

input CaseFilterSetType {
  workflow: ID
  createdByUser: String
  createdByGroup: String
  metaHasKey: String
  metaValue: [JSONValueFilterType]
  orderBy: [CaseOrdering]
  documentForm: String
  hasAnswer: [HasAnswerFilterType]
  workItemDocumentHasAnswer: [HasAnswerFilterType]
  rootCase: ID
  searchAnswers: [SearchAnswersFilterType]
  status: [CaseStatusArgument]
  orderByQuestionAnswerValue: String
  invert: Boolean
}

input CaseOrderSetType {
  meta: String
  attribute: SortableCaseAttributes
  documentAnswer: String
  direction: AscDesc
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
  META_TEST_KEY_ASC
  META_TEST_KEY_DESC
  META_FOOBAR_ASC
  META_FOOBAR_DESC
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
  infoText: String
  meta: GenericScalar!
  source: Question
  forms(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, createdByUser: String, createdByGroup: String, metaHasKey: String, search: String, slugs: [String]): FormConnection
  options(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], slug: String, label: String, isArchived: Boolean, createdByUser: String, createdByGroup: String, metaHasKey: String, search: String, orderBy: [OptionOrdering]): OptionConnection
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
  meta: GenericScalar!
  addressGroups: GroupJexl
  controlGroups: GroupJexl
  isArchived: Boolean!
  leadTime: Int
  isMultipleInstance: Boolean!
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
  meta: GenericScalar!
  addressGroups: GroupJexl
  controlGroups: GroupJexl
  isArchived: Boolean!
  leadTime: Int
  isMultipleInstance: Boolean!
  id: ID!
}

input CopyDocumentInput {
  source: ID!
  clientMutationId: String
}

type CopyDocumentPayload {
  document: Document
  clientMutationId: String
}

input CopyFormInput {
  slug: String!
  name: String!
  description: String
  source: ID!
  isPublished: Boolean
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

input CreateWorkItemInput {
  case: ID!
  multipleInstanceTask: ID!
  name: String
  description: String
  assignedUsers: [String]
  addressedGroups: [String]
  controllingGroups: [String]
  deadline: DateTime
  meta: JSONString
  clientMutationId: String
}

type CreateWorkItemPayload {
  workItem: WorkItem
  clientMutationId: String
}

type DataSource {
  info: String
  name: String!
}

type DataSourceConnection {
  pageInfo: PageInfo!
  edges: [DataSourceEdge]!
  totalCount: Int
}

type DataSourceData {
  label: String!
  slug: String!
}

type DataSourceDataConnection {
  pageInfo: PageInfo!
  edges: [DataSourceDataEdge]!
  totalCount: Int
}

type DataSourceDataEdge {
  node: DataSourceData
  cursor: String!
}

type DataSourceEdge {
  node: DataSource
  cursor: String!
}

scalar Date

type DateAnswer implements Answer, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  question: Question!
  value: Date
  meta: GenericScalar!
  date: Date
}

type DateQuestion implements Question, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  slug: String!
  label: String!
  isRequired: QuestionJexl!
  isHidden: QuestionJexl!
  isArchived: Boolean!
  infoText: String
  meta: GenericScalar!
  source: Question
  forms(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, createdByUser: String, createdByGroup: String, metaHasKey: String, search: String, slugs: [String]): FormConnection
  id: ID!
}

scalar DateTime

type DjangoDebug {
  sql: [DjangoDebugSQL]
}

type DjangoDebugSQL {
  vendor: String!
  alias: String!
  sql: String
  duration: Float!
  rawSql: String!
  params: String!
  startTime: Float!
  stopTime: Float!
  isSlow: Boolean!
  isSelect: Boolean!
  transId: String
  transStatus: String
  isoLevel: String
  encoding: String
}

type Document implements Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  form: Form!
  source: Document
  meta: GenericScalar
  copies(before: String, after: String, first: Int, last: Int): DocumentConnection!
  answers(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], question: ID, search: String, orderBy: [AnswerOrdering], filter: [AnswerFilterSetType], order: [AnswerOrderSetType], createdByUser: String, createdByGroup: String, metaHasKey: String, questions: [ID], visibleInContext: Boolean): AnswerConnection
  case: Case
  workItem: WorkItem
}

type DocumentConnection {
  pageInfo: PageInfo!
  edges: [DocumentEdge]!
  totalCount: Int
}

type DocumentEdge {
  node: Document
  cursor: String!
}

input DocumentFilterSetType {
  form: ID
  forms: [ID]
  search: String
  id: ID
  createdByUser: String
  createdByGroup: String
  metaHasKey: String
  metaValue: [JSONValueFilterType]
  orderBy: [DocumentOrdering]
  rootDocument: ID
  hasAnswer: [HasAnswerFilterType]
  searchAnswers: [SearchAnswersFilterType]
  invert: Boolean
}

input DocumentOrderSetType {
  meta: String
  answerValue: String
  attribute: SortableDocumentAttributes
  direction: AscDesc
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
  META_TEST_KEY_ASC
  META_TEST_KEY_DESC
  META_FOOBAR_ASC
  META_FOOBAR_DESC
}

type DocumentValidityConnection {
  pageInfo: PageInfo!
  edges: [DocumentValidityEdge]!
  totalCount: Int
}

type DocumentValidityEdge {
  node: ValidationResult
  cursor: String!
}

type DynamicChoiceQuestion implements Question, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  slug: String!
  label: String!
  isRequired: QuestionJexl!
  isHidden: QuestionJexl!
  isArchived: Boolean!
  infoText: String
  meta: GenericScalar!
  source: Question
  forms(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, createdByUser: String, createdByGroup: String, metaHasKey: String, search: String, slugs: [String]): FormConnection
  options(before: String, after: String, first: Int, last: Int): DataSourceDataConnection
  dataSource: String!
  id: ID!
}

type DynamicMultipleChoiceQuestion implements Question, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  slug: String!
  label: String!
  isRequired: QuestionJexl!
  isHidden: QuestionJexl!
  isArchived: Boolean!
  infoText: String
  meta: GenericScalar!
  source: Question
  forms(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, createdByUser: String, createdByGroup: String, metaHasKey: String, search: String, slugs: [String]): FormConnection
  options(before: String, after: String, first: Int, last: Int): DataSourceDataConnection
  dataSource: String!
  id: ID!
}

type DynamicOption implements Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  slug: String!
  label: String!
  document: Document!
  question: StaticQuestion!
}

type DynamicOptionConnection {
  pageInfo: PageInfo!
  edges: [DynamicOptionEdge]!
  totalCount: Int
}

type DynamicOptionEdge {
  node: DynamicOption
  cursor: String!
}

input DynamicOptionFilterSetType {
  question: ID
  document: ID
  invert: Boolean
}

type File implements Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  name: String!
  answer: FileAnswer
  uploadUrl: String
  downloadUrl: String
  metadata: GenericScalar
}

type FileAnswer implements Answer, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  question: Question!
  value: File!
  meta: GenericScalar!
  file: File
}

type FileQuestion implements Question, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  slug: String!
  label: String!
  isRequired: QuestionJexl!
  isHidden: QuestionJexl!
  isArchived: Boolean!
  infoText: String
  meta: GenericScalar!
  source: Question
  forms(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, createdByUser: String, createdByGroup: String, metaHasKey: String, search: String, slugs: [String]): FormConnection
  id: ID!
}

type FloatAnswer implements Answer, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  question: Question!
  value: Float
  meta: GenericScalar!
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
  placeholder: String
  infoText: String
  meta: GenericScalar!
  source: Question
  forms(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, createdByUser: String, createdByGroup: String, metaHasKey: String, search: String, slugs: [String]): FormConnection
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
  totalCount: Int
}

type FlowEdge {
  node: Flow
  cursor: String!
}

input FlowFilterSetType {
  task: ID
  createdByUser: String
  createdByGroup: String
  invert: Boolean
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
  meta: GenericScalar
  isPublished: Boolean!
  isArchived: Boolean!
  questions(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], slug: String, label: String, isRequired: String, isHidden: String, isArchived: Boolean, createdByUser: String, createdByGroup: String, metaHasKey: String, excludeForms: [ID], search: String, orderBy: [QuestionOrdering], slugs: [String]): QuestionConnection
  source: Form
  documents(before: String, after: String, first: Int, last: Int): DocumentConnection!
  id: ID!
}

type FormConnection {
  pageInfo: PageInfo!
  edges: [FormEdge]!
  totalCount: Int
}

type FormEdge {
  node: Form
  cursor: String!
}

input FormFilterSetType {
  orderBy: [FormOrdering]
  slug: String
  name: String
  description: String
  isPublished: Boolean
  isArchived: Boolean
  createdByUser: String
  createdByGroup: String
  metaHasKey: String
  metaValue: [JSONValueFilterType]
  search: String
  slugs: [String]
  invert: Boolean
}

input FormOrderSetType {
  meta: String
  attribute: SortableFormAttributes
  direction: AscDesc
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
  META_TEST_KEY_ASC
  META_TEST_KEY_DESC
  META_FOOBAR_ASC
  META_FOOBAR_DESC
}

type FormQuestion implements Question, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  slug: String!
  label: String!
  isRequired: QuestionJexl!
  isHidden: QuestionJexl!
  isArchived: Boolean!
  infoText: String
  meta: GenericScalar!
  source: Question
  forms(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, createdByUser: String, createdByGroup: String, metaHasKey: String, search: String, slugs: [String]): FormConnection
  subForm: Form
  id: ID!
}

type FormatValidator {
  slug: String!
  name: String!
  regex: String!
  errorMsg: String!
}

type FormatValidatorConnection {
  pageInfo: PageInfo!
  edges: [FormatValidatorEdge]!
  totalCount: Int
}

type FormatValidatorEdge {
  node: FormatValidator
  cursor: String!
}

scalar GenericScalar

scalar GroupJexl

input HasAnswerFilterType {
  question: ID!
  value: GenericScalar
  lookup: AnswerLookupMode
  hierarchy: AnswerHierarchyMode
}

interface HistoricalAnswer {
  id: ID
  createdAt: DateTime!
  createdByUser: String
  createdByGroup: String
  modifiedAt: DateTime!
  question: Question!
  meta: GenericScalar!
  historyDate: DateTime!
  historyUserId: String
  historyType: String
}

type HistoricalAnswerConnection {
  pageInfo: PageInfo!
  edges: [HistoricalAnswerEdge]!
  totalCount: Int
}

type HistoricalAnswerEdge {
  node: HistoricalAnswer
  cursor: String!
}

type HistoricalDateAnswer implements HistoricalAnswer, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  value: Date
  meta: GenericScalar!
  date: Date
  historyUserId: String
  question: Question!
  historyId: UUID!
  historyDate: DateTime!
  historyChangeReason: String
  historyType: String
}

type HistoricalDocument implements Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  meta: GenericScalar
  historyUserId: String
  form: Form
  source: Document
  historyDate: DateTime!
  historyType: String
  historicalAnswers(asOf: DateTime!, before: String, after: String, first: Int, last: Int): HistoricalAnswerConnection
  documentId: UUID
}

type HistoricalFile implements Node {
  id: ID!
  name: String!
  downloadUrl: String
  metadata: GenericScalar
  historicalAnswer: HistoricalFileAnswer
  historyDate: DateTime!
  historyUserId: String
  historyType: String
}

type HistoricalFileAnswer implements HistoricalAnswer, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  value(asOf: DateTime!): HistoricalFile
  meta: GenericScalar!
  historyUserId: String
  question: Question!
  historyId: UUID!
  historyDate: DateTime!
  historyChangeReason: String
  historyType: String
  file: File
}

type HistoricalFloatAnswer implements HistoricalAnswer, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  value: Float
  meta: GenericScalar!
  historyUserId: String
  question: Question!
  historyId: UUID!
  historyDate: DateTime!
  historyChangeReason: String
  historyType: String
}

type HistoricalIntegerAnswer implements HistoricalAnswer, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  value: Int
  meta: GenericScalar!
  historyUserId: String
  question: Question!
  historyId: UUID!
  historyDate: DateTime!
  historyChangeReason: String
  historyType: String
}

type HistoricalListAnswer implements HistoricalAnswer, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  value: [String]
  meta: GenericScalar!
  historyUserId: String
  question: Question!
  historyId: UUID!
  historyDate: DateTime!
  historyChangeReason: String
  historyType: String
}

type HistoricalStringAnswer implements HistoricalAnswer, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  value: String
  meta: GenericScalar!
  historyUserId: String
  question: Question!
  historyId: UUID!
  historyDate: DateTime!
  historyChangeReason: String
  historyType: String
}

type HistoricalTableAnswer implements HistoricalAnswer, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  value(asOf: DateTime!): [HistoricalDocument]
  meta: GenericScalar!
  historyUserId: String
  question: Question!
  historyId: UUID!
  historyDate: DateTime!
  historyChangeReason: String
  historyType: String
  document: Document
}

type IntegerAnswer implements Answer, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  question: Question!
  value: Int
  meta: GenericScalar!
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
  placeholder: String
  infoText: String
  meta: GenericScalar!
  source: Question
  forms(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, createdByUser: String, createdByGroup: String, metaHasKey: String, search: String, slugs: [String]): FormConnection
  id: ID!
  maxValue: Int
  minValue: Int
}

enum JSONLookupMode {
  EXACT
  STARTSWITH
  CONTAINS
  ICONTAINS
  GTE
  GT
  LTE
  LT
}

scalar JSONString

input JSONValueFilterType {
  key: String!
  value: GenericScalar!
  lookup: JSONLookupMode
}

type ListAnswer implements Answer, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  question: Question!
  value: [String]
  meta: GenericScalar!
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
  infoText: String
  meta: GenericScalar!
  source: Question
  forms(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, createdByUser: String, createdByGroup: String, metaHasKey: String, search: String, slugs: [String]): FormConnection
  options(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], orderBy: [OptionOrdering], slug: String, label: String, isArchived: Boolean, createdByUser: String, createdByGroup: String, metaHasKey: String, search: String): OptionConnection
  staticContent: String
  id: ID!
}

type Mutation {
  saveWorkflow(input: SaveWorkflowInput!): SaveWorkflowPayload
  addWorkflowFlow(input: AddWorkflowFlowInput!): AddWorkflowFlowPayload
  removeFlow(input: RemoveFlowInput!): RemoveFlowPayload
  saveSimpleTask(input: SaveSimpleTaskInput!): SaveSimpleTaskPayload
  saveCompleteWorkflowFormTask(input: SaveCompleteWorkflowFormTaskInput!): SaveCompleteWorkflowFormTaskPayload
  saveCompleteTaskFormTask(input: SaveCompleteTaskFormTaskInput!): SaveCompleteTaskFormTaskPayload
  startCase(input: StartCaseInput!): StartCasePayload @deprecated(reason: "Use SaveCase mutation instead")
  saveCase(input: SaveCaseInput!): SaveCasePayload
  cancelCase(input: CancelCaseInput!): CancelCasePayload
  completeWorkItem(input: CompleteWorkItemInput!): CompleteWorkItemPayload
  skipWorkItem(input: SkipWorkItemInput!): SkipWorkItemPayload
  saveWorkItem(input: SaveWorkItemInput!): SaveWorkItemPayload
  createWorkItem(input: CreateWorkItemInput!): CreateWorkItemPayload
  saveForm(input: SaveFormInput!): SaveFormPayload
  copyForm(input: CopyFormInput!): CopyFormPayload
  addFormQuestion(input: AddFormQuestionInput!): AddFormQuestionPayload
  removeFormQuestion(input: RemoveFormQuestionInput!): RemoveFormQuestionPayload
  reorderFormQuestions(input: ReorderFormQuestionsInput!): ReorderFormQuestionsPayload
  saveOption(input: SaveOptionInput!): SaveOptionPayload
  copyOption(input: CopyOptionInput!): CopyOptionPayload
  copyQuestion(input: CopyQuestionInput!): CopyQuestionPayload
  saveTextQuestion(input: SaveTextQuestionInput!): SaveTextQuestionPayload
  saveTextareaQuestion(input: SaveTextareaQuestionInput!): SaveTextareaQuestionPayload
  saveDateQuestion(input: SaveDateQuestionInput!): SaveDateQuestionPayload
  saveChoiceQuestion(input: SaveChoiceQuestionInput!): SaveChoiceQuestionPayload
  saveMultipleChoiceQuestion(input: SaveMultipleChoiceQuestionInput!): SaveMultipleChoiceQuestionPayload
  saveDynamicChoiceQuestion(input: SaveDynamicChoiceQuestionInput!): SaveDynamicChoiceQuestionPayload
  saveDynamicMultipleChoiceQuestion(input: SaveDynamicMultipleChoiceQuestionInput!): SaveDynamicMultipleChoiceQuestionPayload
  saveFloatQuestion(input: SaveFloatQuestionInput!): SaveFloatQuestionPayload
  saveIntegerQuestion(input: SaveIntegerQuestionInput!): SaveIntegerQuestionPayload
  saveTableQuestion(input: SaveTableQuestionInput!): SaveTableQuestionPayload
  saveFormQuestion(input: SaveFormQuestionInput!): SaveFormQuestionPayload
  saveFileQuestion(input: SaveFileQuestionInput!): SaveFileQuestionPayload
  saveStaticQuestion(input: SaveStaticQuestionInput!): SaveStaticQuestionPayload
  copyDocument(input: CopyDocumentInput!): CopyDocumentPayload
  saveDocument(input: SaveDocumentInput!): SaveDocumentPayload
  saveDocumentStringAnswer(input: SaveDocumentStringAnswerInput!): SaveDocumentStringAnswerPayload
  saveDocumentIntegerAnswer(input: SaveDocumentIntegerAnswerInput!): SaveDocumentIntegerAnswerPayload
  saveDocumentFloatAnswer(input: SaveDocumentFloatAnswerInput!): SaveDocumentFloatAnswerPayload
  saveDocumentDateAnswer(input: SaveDocumentDateAnswerInput!): SaveDocumentDateAnswerPayload
  saveDocumentListAnswer(input: SaveDocumentListAnswerInput!): SaveDocumentListAnswerPayload
  saveDocumentTableAnswer(input: SaveDocumentTableAnswerInput!): SaveDocumentTableAnswerPayload
  saveDocumentFileAnswer(input: SaveDocumentFileAnswerInput!): SaveDocumentFileAnswerPayload
  removeAnswer(input: RemoveAnswerInput!): RemoveAnswerPayload
  removeDocument(input: RemoveDocumentInput!): RemoveDocumentPayload
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
  isArchived: Boolean!
  meta: GenericScalar
  source: Option
  id: ID!
}

type OptionConnection {
  pageInfo: PageInfo!
  edges: [OptionEdge]!
  totalCount: Int
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
  META_TEST_KEY_ASC
  META_TEST_KEY_DESC
  META_FOOBAR_ASC
  META_FOOBAR_DESC
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

type Query {
  documentAsOf(id: ID!, asOf: DateTime!): HistoricalDocument
  allDataSources(before: String, after: String, first: Int, last: Int): DataSourceConnection
  dataSource(name: String!, before: String, after: String, first: Int, last: Int): DataSourceDataConnection
  allWorkflows(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, orderBy: [WorkflowOrdering], filter: [WorkflowFilterSetType], order: [WorkflowOrderSetType], createdByUser: String, createdByGroup: String, metaHasKey: String, search: String): WorkflowConnection
  allTasks(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], slug: String, name: String, description: String, type: TaskTypeArgument, isArchived: Boolean, orderBy: [TaskOrdering], filter: [TaskFilterSetType], order: [TaskOrderSetType], createdByUser: String, createdByGroup: String, metaHasKey: String, search: String): TaskConnection
  allCases(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], workflow: ID, orderBy: [CaseOrdering], filter: [CaseFilterSetType], order: [CaseOrderSetType], createdByUser: String, createdByGroup: String, metaHasKey: String, documentForm: String, hasAnswer: [HasAnswerFilterType], workItemDocumentHasAnswer: [HasAnswerFilterType], rootCase: ID, searchAnswers: [SearchAnswersFilterType], status: [CaseStatusArgument], orderByQuestionAnswerValue: String): CaseConnection
  allWorkItems(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], status: WorkItemStatusArgument, orderBy: [WorkItemOrdering], filter: [WorkItemFilterSetType], order: [WorkItemOrderSetType], documentHasAnswer: [HasAnswerFilterType], caseDocumentHasAnswer: [HasAnswerFilterType], caseMetaValue: [JSONValueFilterType], name: String, task: ID, case: ID, createdAt: DateTime, closedAt: DateTime, modifiedAt: DateTime, createdByUser: String, createdByGroup: String, metaHasKey: String, addressedGroups: [String], controllingGroups: [String], assignedUsers: [String]): WorkItemConnection
  allForms(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, filter: [FormFilterSetType], order: [FormOrderSetType], createdByUser: String, createdByGroup: String, metaHasKey: String, search: String, slugs: [String]): FormConnection
  allQuestions(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], orderBy: [QuestionOrdering], slug: String, label: String, isRequired: String, isHidden: String, isArchived: Boolean, filter: [QuestionFilterSetType], order: [QuestionOrderSetType], createdByUser: String, createdByGroup: String, metaHasKey: String, excludeForms: [ID], search: String, slugs: [String]): QuestionConnection
  allDocuments(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], form: ID, forms: [ID], search: String, id: ID, orderBy: [DocumentOrdering], filter: [DocumentFilterSetType], order: [DocumentOrderSetType], createdByUser: String, createdByGroup: String, metaHasKey: String, rootDocument: ID, hasAnswer: [HasAnswerFilterType], searchAnswers: [SearchAnswersFilterType]): DocumentConnection
  allFormatValidators(before: String, after: String, first: Int, last: Int): FormatValidatorConnection
  allUsedDynamicOptions(before: String, after: String, first: Int, last: Int, question: ID, document: ID, filter: [DynamicOptionFilterSetType], createdByUser: String, createdByGroup: String): DynamicOptionConnection
  documentValidity(id: ID!, before: String, after: String, first: Int, last: Int): DocumentValidityConnection
  node(id: ID!): Node
  _debug: DjangoDebug
}

interface Question {
  id: ID!
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  slug: String!
  label: String!
  infoText: String
  isRequired: QuestionJexl!
  isHidden: QuestionJexl!
  isArchived: Boolean!
  meta: GenericScalar!
  forms(before: String, after: String, first: Int, last: Int, slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, createdByUser: String, createdByGroup: String, metaHasKey: String, metaValue: [JSONValueFilterType], search: String, orderBy: [FormOrdering], slugs: [String]): FormConnection
  source: Question
}

type QuestionConnection {
  pageInfo: PageInfo!
  edges: [QuestionEdge]!
  totalCount: Int
}

type QuestionEdge {
  node: Question
  cursor: String!
}

input QuestionFilterSetType {
  orderBy: [QuestionOrdering]
  slug: String
  label: String
  isRequired: String
  isHidden: String
  isArchived: Boolean
  createdByUser: String
  createdByGroup: String
  metaHasKey: String
  metaValue: [JSONValueFilterType]
  excludeForms: [ID]
  search: String
  slugs: [String]
  invert: Boolean
}

scalar QuestionJexl

input QuestionOrderSetType {
  meta: String
  attribute: SortableQuestionAttributes
  direction: AscDesc
}

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
  META_TEST_KEY_ASC
  META_TEST_KEY_DESC
  META_FOOBAR_ASC
  META_FOOBAR_DESC
}

input RemoveAnswerInput {
  answer: ID!
  clientMutationId: String
}

type RemoveAnswerPayload {
  answer: Answer
  clientMutationId: String
}

input RemoveDocumentInput {
  document: ID!
  clientMutationId: String
}

type RemoveDocumentPayload {
  document: Document
  clientMutationId: String
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

input ReorderFormQuestionsInput {
  form: ID!
  questions: [ID]!
  clientMutationId: String
}

type ReorderFormQuestionsPayload {
  form: Form
  clientMutationId: String
}

input SaveCaseInput {
  id: String
  workflow: ID!
  meta: JSONString
  parentWorkItem: ID
  form: ID
  clientMutationId: String
}

type SaveCasePayload {
  case: Case
  clientMutationId: String
}

input SaveChoiceQuestionInput {
  slug: String!
  label: String!
  infoText: String
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
  controlGroups: GroupJexl
  isArchived: Boolean
  leadTime: Int
  isMultipleInstance: Boolean
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
  controlGroups: GroupJexl
  isArchived: Boolean
  leadTime: Int
  isMultipleInstance: Boolean
  clientMutationId: String
}

type SaveCompleteWorkflowFormTaskPayload {
  task: Task
  clientMutationId: String
}

input SaveDateQuestionInput {
  slug: String!
  label: String!
  infoText: String
  isRequired: QuestionJexl
  isHidden: QuestionJexl
  meta: JSONString
  isArchived: Boolean
  clientMutationId: String
}

type SaveDateQuestionPayload {
  question: Question
  clientMutationId: String
}

input SaveDocumentDateAnswerInput {
  question: ID!
  document: ID!
  meta: JSONString
  value: Date
  clientMutationId: String
}

type SaveDocumentDateAnswerPayload {
  answer: Answer
  clientMutationId: String
}

input SaveDocumentFileAnswerInput {
  question: ID!
  document: ID!
  meta: JSONString
  value: String
  valueId: ID
  clientMutationId: String
}

type SaveDocumentFileAnswerPayload {
  answer: Answer
  clientMutationId: String
}

input SaveDocumentFloatAnswerInput {
  question: ID!
  document: ID!
  meta: JSONString
  value: Float
  clientMutationId: String
}

type SaveDocumentFloatAnswerPayload {
  answer: Answer
  clientMutationId: String
}

input SaveDocumentInput {
  id: String
  form: ID!
  meta: JSONString
  clientMutationId: String
}

input SaveDocumentIntegerAnswerInput {
  question: ID!
  document: ID!
  meta: JSONString
  value: Int
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
  value: [String]
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
  value: String
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
  value: [ID]
  clientMutationId: String
}

type SaveDocumentTableAnswerPayload {
  answer: Answer
  clientMutationId: String
}

input SaveDynamicChoiceQuestionInput {
  slug: String!
  label: String!
  infoText: String
  isRequired: QuestionJexl
  isHidden: QuestionJexl
  meta: JSONString
  isArchived: Boolean
  dataSource: String!
  clientMutationId: String
}

type SaveDynamicChoiceQuestionPayload {
  question: Question
  clientMutationId: String
}

input SaveDynamicMultipleChoiceQuestionInput {
  slug: String!
  label: String!
  infoText: String
  isRequired: QuestionJexl
  isHidden: QuestionJexl
  meta: JSONString
  isArchived: Boolean
  dataSource: String!
  clientMutationId: String
}

type SaveDynamicMultipleChoiceQuestionPayload {
  question: Question
  clientMutationId: String
}

input SaveFileQuestionInput {
  slug: String!
  label: String!
  infoText: String
  isRequired: QuestionJexl
  isHidden: QuestionJexl
  meta: JSONString
  isArchived: Boolean
  clientMutationId: String
}

type SaveFileQuestionPayload {
  question: Question
  clientMutationId: String
}

input SaveFloatQuestionInput {
  slug: String!
  label: String!
  infoText: String
  isRequired: QuestionJexl
  isHidden: QuestionJexl
  meta: JSONString
  isArchived: Boolean
  minValue: Float
  maxValue: Float
  placeholder: String
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

input SaveFormQuestionInput {
  slug: String!
  label: String!
  infoText: String
  isRequired: QuestionJexl
  isHidden: QuestionJexl
  meta: JSONString
  isArchived: Boolean
  subForm: ID!
  clientMutationId: String
}

type SaveFormQuestionPayload {
  question: Question
  clientMutationId: String
}

input SaveIntegerQuestionInput {
  slug: String!
  label: String!
  infoText: String
  isRequired: QuestionJexl
  isHidden: QuestionJexl
  meta: JSONString
  isArchived: Boolean
  minValue: Int
  maxValue: Int
  placeholder: String
  clientMutationId: String
}

type SaveIntegerQuestionPayload {
  question: Question
  clientMutationId: String
}

input SaveMultipleChoiceQuestionInput {
  slug: String!
  label: String!
  infoText: String
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
  isArchived: Boolean
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
  controlGroups: GroupJexl
  isArchived: Boolean
  leadTime: Int
  isMultipleInstance: Boolean
  clientMutationId: String
}

type SaveSimpleTaskPayload {
  task: Task
  clientMutationId: String
}

input SaveStaticQuestionInput {
  label: String!
  slug: String!
  infoText: String
  isHidden: QuestionJexl
  meta: JSONString
  isArchived: Boolean
  staticContent: String
  clientMutationId: String
}

type SaveStaticQuestionPayload {
  question: Question
  clientMutationId: String
}

input SaveTableQuestionInput {
  slug: String!
  label: String!
  infoText: String
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
  infoText: String
  isRequired: QuestionJexl
  isHidden: QuestionJexl
  meta: JSONString
  isArchived: Boolean
  minLength: Int
  maxLength: Int
  placeholder: String
  formatValidators: [String]
  clientMutationId: String
}

type SaveTextQuestionPayload {
  question: Question
  clientMutationId: String
}

input SaveTextareaQuestionInput {
  slug: String!
  label: String!
  infoText: String
  isRequired: QuestionJexl
  isHidden: QuestionJexl
  meta: JSONString
  isArchived: Boolean
  minLength: Int
  maxLength: Int
  placeholder: String
  formatValidators: [String]
  clientMutationId: String
}

type SaveTextareaQuestionPayload {
  question: Question
  clientMutationId: String
}

input SaveWorkItemInput {
  workItem: ID!
  name: String
  description: String
  assignedUsers: [String]
  deadline: DateTime
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

input SearchAnswersFilterType {
  questions: [ID]
  value: GenericScalar!
  lookup: SearchLookupMode
}

enum SearchLookupMode {
  STARTSWITH
  CONTAINS
  TEXT
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
  meta: GenericScalar!
  addressGroups: GroupJexl
  controlGroups: GroupJexl
  isArchived: Boolean!
  leadTime: Int
  isMultipleInstance: Boolean!
  id: ID!
}

input SkipWorkItemInput {
  id: ID!
  clientMutationId: String
}

type SkipWorkItemPayload {
  workItem: WorkItem
  clientMutationId: String
}

enum SortableAnswerAttributes {
  CREATED_AT
  MODIFIED_AT
  CREATED_BY_USER
  CREATED_BY_GROUP
  QUESTION
  VALUE
  DOCUMENT
  DATE
  FILE
}

enum SortableCaseAttributes {
  ALLOW_ALL_FORMS
  CREATED_BY_GROUP
  CREATED_BY_USER
  DESCRIPTION
  IS_ARCHIVED
  IS_PUBLISHED
  NAME
  STATUS
  SLUG
}

enum SortableDocumentAttributes {
  CREATED_AT
  MODIFIED_AT
  CREATED_BY_USER
  CREATED_BY_GROUP
  FORM
  SOURCE
}

enum SortableFormAttributes {
  CREATED_AT
  MODIFIED_AT
  CREATED_BY_USER
  CREATED_BY_GROUP
  SLUG
  NAME
  DESCRIPTION
  IS_PUBLISHED
  IS_ARCHIVED
}

enum SortableQuestionAttributes {
  CREATED_AT
  MODIFIED_AT
  CREATED_BY_USER
  CREATED_BY_GROUP
  SLUG
  LABEL
  TYPE
  IS_REQUIRED
  IS_HIDDEN
  IS_ARCHIVED
  PLACEHOLDER
  INFO_TEXT
}

enum SortableTaskAttributes {
  ALLOW_ALL_FORMS
  LEAD_TIME
  TYPE
  CREATED_BY_GROUP
  CREATED_BY_USER
  DESCRIPTION
  IS_ARCHIVED
  IS_PUBLISHED
  NAME
  SLUG
}

enum SortableWorkItemAttributes {
  ALLOW_ALL_FORMS
  CREATED_BY_GROUP
  CREATED_BY_USER
  DESCRIPTION
  CREATED_AT
  MODIFIED_AT
  CLOSED_AT
  IS_ARCHIVED
  IS_PUBLISHED
  NAME
  DEADLINE
  STATUS
  SLUG
}

enum SortableWorkflowAttributes {
  ALLOW_ALL_FORMS
  CREATED_BY_GROUP
  CREATED_BY_USER
  DESCRIPTION
  IS_ARCHIVED
  IS_PUBLISHED
  NAME
  SLUG
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

type StaticQuestion implements Question, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  slug: String!
  label: String!
  isRequired: QuestionJexl!
  isHidden: QuestionJexl!
  isArchived: Boolean!
  infoText: String
  meta: GenericScalar!
  source: Question
  forms(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, createdByUser: String, createdByGroup: String, metaHasKey: String, search: String, slugs: [String]): FormConnection
  staticContent: String
  dataSource: String
  id: ID!
}

enum Status {
  READY
  COMPLETED
  CANCELED
  SKIPPED
}

type StringAnswer implements Answer, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  question: Question!
  value: String
  meta: GenericScalar!
}

type TableAnswer implements Answer, Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  question: Question!
  value: [Document]
  meta: GenericScalar!
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
  infoText: String
  meta: GenericScalar!
  source: Question
  forms(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, createdByUser: String, createdByGroup: String, metaHasKey: String, search: String, slugs: [String]): FormConnection
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
  controlGroups: GroupJexl
  meta: GenericScalar!
  isMultipleInstance: Boolean!
}

type TaskConnection {
  pageInfo: PageInfo!
  edges: [TaskEdge]!
  totalCount: Int
}

type TaskEdge {
  node: Task
  cursor: String!
}

input TaskFilterSetType {
  slug: String
  name: String
  description: String
  type: Type
  isArchived: Boolean
  createdByUser: String
  createdByGroup: String
  metaHasKey: String
  metaValue: [JSONValueFilterType]
  search: String
  orderBy: [TaskOrdering]
  invert: Boolean
}

input TaskOrderSetType {
  meta: String
  attribute: SortableTaskAttributes
  direction: AscDesc
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
  META_TEST_KEY_ASC
  META_TEST_KEY_DESC
  META_FOOBAR_ASC
  META_FOOBAR_DESC
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
  placeholder: String
  infoText: String
  meta: GenericScalar!
  source: Question
  formatValidators(before: String, after: String, first: Int, last: Int): FormatValidatorConnection
  forms(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, createdByUser: String, createdByGroup: String, metaHasKey: String, search: String, slugs: [String]): FormConnection
  id: ID!
  minLength: Int
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
  placeholder: String
  infoText: String
  meta: GenericScalar!
  source: Question
  formatValidators(before: String, after: String, first: Int, last: Int): FormatValidatorConnection
  forms(before: String, after: String, first: Int, last: Int, metaValue: [JSONValueFilterType], orderBy: [FormOrdering], slug: String, name: String, description: String, isPublished: Boolean, isArchived: Boolean, createdByUser: String, createdByGroup: String, metaHasKey: String, search: String, slugs: [String]): FormConnection
  id: ID!
  minLength: Int
  maxLength: Int
}

enum Type {
  SIMPLE
  COMPLETE_WORKFLOW_FORM
  COMPLETE_TASK_FORM
}

scalar UUID

type ValidationEntry {
  slug: String!
  errorMsg: String!
}

type ValidationResult {
  id: ID
  isValid: Boolean
  errors: [ValidationEntry]
}

type WorkItem implements Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  id: ID!
  name: String!
  description: String
  closedAt: DateTime
  closedByUser: String
  closedByGroup: String
  deadline: DateTime
  task: Task!
  status: WorkItemStatus!
  meta: GenericScalar
  addressedGroups: [String]!
  controllingGroups: [String]!
  assignedUsers: [String]!
  case: Case!
  childCase: Case
  document: Document
}

type WorkItemConnection {
  pageInfo: PageInfo!
  edges: [WorkItemEdge]!
  totalCount: Int
}

type WorkItemEdge {
  node: WorkItem
  cursor: String!
}

input WorkItemFilterSetType {
  status: Status
  name: String
  task: ID
  case: ID
  createdAt: DateTime
  closedAt: DateTime
  modifiedAt: DateTime
  createdByUser: String
  createdByGroup: String
  metaHasKey: String
  metaValue: [JSONValueFilterType]
  orderBy: [WorkItemOrdering]
  addressedGroups: [String]
  controllingGroups: [String]
  assignedUsers: [String]
  documentHasAnswer: [HasAnswerFilterType]
  caseDocumentHasAnswer: [HasAnswerFilterType]
  caseMetaValue: [JSONValueFilterType]
  invert: Boolean
}

input WorkItemOrderSetType {
  meta: String
  caseMeta: String
  attribute: SortableWorkItemAttributes
  documentAnswer: String
  caseDocumentAnswer: String
  direction: AscDesc
}

enum WorkItemOrdering {
  STATUS_ASC
  STATUS_DESC
  DEADLINE_ASC
  DEADLINE_DESC
  CREATED_AT_ASC
  CREATED_AT_DESC
  MODIFIED_AT_ASC
  MODIFIED_AT_DESC
  CREATED_BY_USER_ASC
  CREATED_BY_USER_DESC
  CREATED_BY_GROUP_ASC
  CREATED_BY_GROUP_DESC
  META_TEST_KEY_ASC
  META_TEST_KEY_DESC
  META_FOOBAR_ASC
  META_FOOBAR_DESC
}

enum WorkItemStatus {
  READY
  COMPLETED
  CANCELED
  SKIPPED
}

enum WorkItemStatusArgument {
  READY
  COMPLETED
  CANCELED
  SKIPPED
}

type Workflow implements Node {
  createdAt: DateTime!
  modifiedAt: DateTime!
  createdByUser: String
  createdByGroup: String
  slug: String!
  name: String!
  description: String
  meta: GenericScalar
  isPublished: Boolean!
  isArchived: Boolean!
  startTasks: [Task]!
  allowAllForms: Boolean!
  allowForms(before: String, after: String, first: Int, last: Int): FormConnection!
  id: ID!
  tasks: [Task]!
  flows(before: String, after: String, first: Int, last: Int, task: ID, filter: [FlowFilterSetType], createdByUser: String, createdByGroup: String): FlowConnection
}

type WorkflowConnection {
  pageInfo: PageInfo!
  edges: [WorkflowEdge]!
  totalCount: Int
}

type WorkflowEdge {
  node: Workflow
  cursor: String!
}

input WorkflowFilterSetType {
  slug: String
  name: String
  description: String
  isPublished: Boolean
  isArchived: Boolean
  createdByUser: String
  createdByGroup: String
  metaHasKey: String
  metaValue: [JSONValueFilterType]
  search: String
  orderBy: [WorkflowOrdering]
  invert: Boolean
}

input WorkflowOrderSetType {
  meta: String
  attribute: SortableWorkflowAttributes
  direction: AscDesc
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
  META_TEST_KEY_ASC
  META_TEST_KEY_DESC
  META_FOOBAR_ASC
  META_FOOBAR_DESC
}
"""
