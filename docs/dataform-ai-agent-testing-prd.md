# Product Requirements Document: AI Agent for Dataform Test Automation

## 1. Executive Summary

### Product Vision
Build an AI agent using Google's Agent Development Kit (ADK) framework to automatically generate comprehensive tests for Google Dataform projects, addressing the critical gap where engineers rarely write tests, leading to code quality issues.

### Primary Goal
Accelerate test creation for Dataform SQLX files and JavaScript utility functions, with emphasis on unit tests using mock data, enabling developers to maintain high code quality without the manual burden of test writing.

---

## 2. Problem Statement

### Current State
- Engineers write Dataform projects (SQLX + JavaScript utility functions)
- Engineers run `dataform compile` and `dataform run`
- **Critical Gap**: Engineers rarely write tests for their Dataform code
- Result: Code quality issues accumulate in production

### Pain Points
- Manual test writing is time-consuming
- Lack of test coverage for SQLX transformations
- JavaScript utility functions go untested
- Individual CTEs within SQLX files aren't tested in isolation
- Integration testing with real data is inconsistent

---

## 3. Target Users

### Primary Users
- Data engineers writing Dataform projects
- Lead data engineer (Python/SQL expertise)

### User Workflow
1. Engineer writes SQLX file with multiple CTEs
2. Engineer writes JavaScript utility functions
3. Engineer compiles and runs Dataform
4. **NEW**: AI agent generates tests automatically
5. Engineer reviews and runs generated tests

---

## 4. Solution Overview

### Core Product
An AI agent built on Google ADK framework that:
- Analyzes Dataform SQLX files and JavaScript utilities
- Generates test cases with mock data
- Focuses on unit testing individual components
- Provides integration test capabilities as secondary feature

### Key Technologies
- **Framework**: Google Agent Development Kit (ADK)
- **Target Code**: 
  - Google Dataform SQLX files
  - JavaScript (Node.js) utility functions
- **Integration**: Works within existing Dataform workflow

---

## 5. Functional Requirements

### 5.1 Test Generation for SQLX Files

#### FR-1.1: CTE-Level Testing (HIGH PRIORITY)
- **Description**: Generate tests for individual CTEs within a single SQLX file
- **Input**: SQLX file with multiple CTEs
- **Output**: Test cases that isolate and test each CTE independently
- **Mock Data**: Agent generates realistic mock data for upstream dependencies
- **Example**:
  ```sql
  -- SQLX file: orders_summary.sqlx
  WITH filtered_orders AS (
    SELECT * FROM ${ref('raw_orders')} WHERE status = 'completed'
  ),
  aggregated AS (
    SELECT customer_id, COUNT(*) as order_count FROM filtered_orders GROUP BY customer_id
  )
  SELECT * FROM aggregated
  ```
  - Agent should generate tests for: `filtered_orders` CTE, `aggregated` CTE, and final output

#### FR-1.2: Full SQLX Pipeline Testing (MEDIUM PRIORITY)
- **Description**: Generate end-to-end tests for complete SQLX files
- **Input**: Complete SQLX transformation
- **Output**: Test that validates entire transformation logic
- **Mock Data**: Mock all upstream table dependencies

#### FR-1.3: Mock Data Generation (HIGH PRIORITY)
- **Description**: AI agent creates realistic mock datasets
- **Requirements**:
  - Infer schema from referenced tables
  - Generate edge cases (nulls, duplicates, boundary values)
  - Create minimal but sufficient test datasets
  - Support various data types (dates, strings, numbers, JSON)

### 5.2 Test Generation for JavaScript Utilities

#### FR-2.1: Function-Level Testing (HIGH PRIORITY)
- **Description**: Generate tests for JavaScript utility functions
- **Input**: JavaScript/Node.js functions used in Dataform
- **Output**: Jest or similar test framework tests
- **Coverage**: Unit tests for individual functions with various input scenarios

#### FR-2.2: Integration with SQLX (MEDIUM PRIORITY)
- **Description**: Test JavaScript functions as used within SQLX context
- **Requirement**: Validate JS functions work correctly when called from SQLX

### 5.3 Test Execution Framework

#### FR-3.1: Test Runner Integration (HIGH PRIORITY)
- **Description**: Tests must be executable within Dataform environment
- **Options to evaluate**:
  - Native Dataform test assertions
  - Custom test runner
  - BigQuery scripting for test execution

#### FR-3.2: Mock Data Injection (HIGH PRIORITY)
- **Description**: Mechanism to replace real table references with mock data
- **Requirement**: Temporary test tables or in-memory datasets

### 5.4 Integration Testing (NICE-TO-HAVE)

#### FR-4.1: Real Data Testing (LOW PRIORITY - Future Phase)
- **Description**: Generate tests that run against actual data in development environment
- **Use Case**: Validate transformations against realistic data volumes and patterns
- **Note**: Secondary focus after mock-based unit testing is established

---

## 6. AI Agent Architecture

### 6.1 Agent Capabilities Using ADK

#### Core Agent Functions:
1. **Code Analysis Agent**
   - Parse SQLX files and extract CTEs
   - Analyze JavaScript utility functions
   - Identify table dependencies
   - Map data lineage

2. **Test Strategy Agent**
   - Determine which tests to generate
   - Identify edge cases and scenarios
   - Prioritize test coverage

3. **Mock Data Generation Agent**
   - Infer schemas from table references
   - Generate realistic test datasets
   - Create edge case data

4. **Test Code Generation Agent**
   - Generate test code in appropriate format
   - Create assertions
   - Structure test suites

5. **Test Orchestration Agent**
   - Coordinate test execution
   - Manage mock data lifecycle
   - Report results

### 6.2 ADK Integration Requirements
- Leverage Google ADK's agent orchestration capabilities
- Use ADK's tool calling for interacting with BigQuery
- Implement ADK's context management for maintaining state
- Utilize ADK's prompt engineering patterns

---

## 7. Technical Requirements

### 7.1 Input Requirements
- Access to Dataform project repository
- Ability to parse SQLX and JavaScript files
- Access to schema information (table structures)
- (Optional) Access to development BigQuery environment

### 7.2 Output Requirements
- Generated test files in standard format
- Mock data files or generation scripts
- Test execution instructions
- Test coverage reports

### 7.3 Integration Points
- **Dataform CLI**: Integrate with compile/run workflow
- **Version Control**: Tests committed alongside code
- **CI/CD**: Tests run in automated pipelines
- **BigQuery**: For schema introspection and test execution

---

## 8. User Workflows

### 8.1 Primary Workflow: Generate Tests for New SQLX
1. Engineer completes SQLX file development
2. Engineer runs: `dataform compile` (existing step)
3. **NEW**: Engineer runs: `adk-agent generate-tests --file definitions/orders_summary.sqlx`
4. AI agent analyzes SQLX structure
5. Agent identifies CTEs and dependencies
6. Agent generates mock data fixtures
7. Agent creates test files
8. Engineer reviews generated tests
9. Engineer runs tests: `dataform test` or custom test runner
10. Engineer commits code + tests

### 8.2 Workflow: Generate Tests for JavaScript Utilities
1. Engineer writes JavaScript utility function
2. **NEW**: Engineer runs: `adk-agent generate-tests --file includes/utils.js`
3. Agent analyzes function signatures and logic
4. Agent generates test cases
5. Engineer reviews and runs tests

### 8.3 Workflow: Batch Test Generation
1. Engineer runs: `adk-agent generate-tests --all`
2. Agent scans entire Dataform project
3. Agent identifies files lacking tests
4. Agent generates tests for all untested code
5. Engineer reviews in bulk and integrates

---

## 9. Success Metrics

### 9.1 Adoption Metrics
- % of SQLX files with generated tests
- % of JavaScript functions with generated tests
- Number of tests generated per week
- Engineer satisfaction scores

### 9.2 Quality Metrics
- Test coverage % (lines of code covered)
- Number of bugs caught by generated tests
- False positive rate of generated tests
- Time saved on manual test writing

### 9.3 Performance Metrics
- Test generation time per file
- Test execution time
- Agent response latency

---

## 10. Non-Functional Requirements

### 10.1 Performance
- Test generation should complete within 2 minutes per SQLX file
- Tests should execute quickly (< 30 seconds per test suite)

### 10.2 Reliability
- Agent should successfully generate runnable tests 90%+ of the time
- Mock data should be valid and realistic

### 10.3 Usability
- Simple CLI interface
- Clear error messages
- Minimal configuration required

### 10.4 Security
- No exposure of sensitive data in mock datasets
- Proper access controls for BigQuery connections

---

## 11. Implementation Phases

### Phase 1: Foundation (Weeks 1-4)
- Set up Google ADK environment
- Build code parsing capabilities for SQLX
- Create basic mock data generation
- Generate simple CTE-level tests

### Phase 2: Enhanced Testing (Weeks 5-8)
- JavaScript utility function testing
- Improved mock data generation (edge cases)
- Full SQLX pipeline testing
- Test execution framework

### Phase 3: Integration & Refinement (Weeks 9-12)
- CI/CD integration
- Batch test generation
- Test coverage reporting
- User feedback incorporation

### Phase 4: Advanced Features (Future)
- Integration testing with real data
- Automatic test maintenance
- Performance testing capabilities
- Cross-file dependency testing

---

## 12. Out of Scope (for Initial Release)

- DBT testing (explicitly stated to focus on Dataform first)
- Automatic test updates when code changes
- Performance testing
- Data quality monitoring
- Production data testing
- Test result analytics dashboard

---

## 13. Open Questions & Decisions Needed

1. **Test Format**: What test framework should we use?
   - Dataform native assertions?
   - Custom Python/JavaScript test framework?
   - BigQuery scripting tests?

2. **Mock Data Storage**: Where should mock data fixtures be stored?
   - Separate files in repository?
   - Inline in test code?
   - Temporary BigQuery tables?

3. **ADK Configuration**: What specific ADK features/models will we leverage?
   - Which LLM models for different agent tasks?
   - Tool calling patterns?
   - Context window management?

4. **CI/CD Integration**: How deeply should tests integrate with existing pipelines?
   - Pre-merge test execution required?
   - Nightly full test suite runs?

5. **Schema Discovery**: How will the agent learn table schemas?
   - BigQuery API introspection?
   - Static configuration files?
   - Both?

---

## 14. Dependencies & Risks

### Dependencies
- Google ADK framework availability and documentation
- Access to Dataform projects repository
- BigQuery development environment
- Schema metadata availability

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| ADK framework limitations | High | Evaluate ADK capabilities early, have fallback to custom framework |
| Generated tests have low quality | High | Implement human review process, iterative improvements |
| Mock data doesn't reflect reality | Medium | Start with simple cases, gradually improve sophistication |
| Engineers don't adopt the tool | High | Focus on UX, demonstrate time savings, integrate into workflow |
| SQLX parsing complexity | Medium | Start with common patterns, expand coverage iteratively |

---

## 15. Next Steps

1. **Validate this PRD** with your team
2. **Prototype ADK integration** - build simple proof of concept
3. **Test SQLX parsing** - ensure we can extract CTEs reliably
4. **Design mock data generation** - start with simple schema inference
5. **Create initial test generator** for one CTE pattern
6. **Gather feedback** from first engineer users
7. **Iterate and expand** based on learnings

---

## Appendix A: Example Use Cases

### Use Case 1: Testing a Simple SQLX File

**Input SQLX File**: `definitions/customer_orders.sqlx`
```sql
config {
  type: "table",
  schema: "analytics"
}

WITH customer_data AS (
  SELECT 
    customer_id,
    email,
    created_at
  FROM ${ref('raw_customers')}
  WHERE status = 'active'
),

order_summary AS (
  SELECT 
    c.customer_id,
    c.email,
    COUNT(o.order_id) as total_orders,
    SUM(o.amount) as total_spent
  FROM customer_data c
  LEFT JOIN ${ref('raw_orders')} o 
    ON c.customer_id = o.customer_id
  GROUP BY c.customer_id, c.email
)

SELECT * FROM order_summary WHERE total_orders > 0
```

**Expected Generated Tests**:
1. Test for `customer_data` CTE with mock `raw_customers` data
2. Test for `order_summary` CTE with mock customers and orders
3. Test for final query output filtering
4. Edge case tests: null values, zero orders, large amounts

### Use Case 2: Testing JavaScript Utility Function

**Input JavaScript File**: `includes/utils.js`
```javascript
function calculateDiscount(orderAmount, customerTier) {
  if (customerTier === 'gold') {
    return orderAmount * 0.2;
  } else if (customerTier === 'silver') {
    return orderAmount * 0.1;
  } else {
    return 0;
  }
}

module.exports = { calculateDiscount };
```

**Expected Generated Tests**:
```javascript
describe('calculateDiscount', () => {
  test('should return 20% discount for gold tier', () => {
    expect(calculateDiscount(100, 'gold')).toBe(20);
  });
  
  test('should return 10% discount for silver tier', () => {
    expect(calculateDiscount(100, 'silver')).toBe(10);
  });
  
  test('should return 0 discount for unknown tier', () => {
    expect(calculateDiscount(100, 'bronze')).toBe(0);
  });
  
  test('should handle zero amount', () => {
    expect(calculateDiscount(0, 'gold')).toBe(0);
  });
});
```

---

## Appendix B: Technology Stack Details

### Google ADK Framework Components
- **Agent Orchestration**: Multi-agent coordination
- **Tool Integration**: BigQuery API, file system access
- **Prompt Management**: Reusable prompt templates
- **Context Handling**: Maintaining state across agent calls
- **Streaming Responses**: Real-time test generation feedback

### Required Libraries & Tools
- **Python Libraries**:
  - `google-cloud-bigquery`: For schema introspection
  - `sqlparse`: For SQL parsing
  - `pytest`: For Python-based test execution
  - `faker`: For generating realistic mock data

- **JavaScript/Node.js**:
  - `@google-cloud/bigquery`: BigQuery client
  - `jest`: For JavaScript test execution
  - `esprima` or `acorn`: For JavaScript parsing

### Development Environment
- **Language**: Python 3.9+
- **Cloud**: Google Cloud Platform
- **Version Control**: Git
- **CI/CD**: Cloud Build or GitHub Actions

---

## Appendix C: Glossary

- **SQLX**: SQL extension format used by Dataform for defining data transformations
- **CTE**: Common Table Expression - a temporary named result set in SQL
- **ADK**: Agent Development Kit - Google's framework for building AI agents
- **Mock Data**: Synthetic data used for testing without accessing real databases
- **Unit Test**: Testing individual components in isolation
- **Integration Test**: Testing multiple components working together
- **Dataform**: Google's data transformation tool for BigQuery
- **BigQuery**: Google's cloud data warehouse

---

**Document Version**: 1.0  
**Last Updated**: October 25, 2025  
**Author**: Lead Data Engineer  
**Status**: Draft for Review
