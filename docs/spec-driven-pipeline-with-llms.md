# Spec-Driven Data Pipelines: Bridging Business Requirements and Code with LLMs

## The Challenge: From Ambiguity to Execution

Data engineering teams face a recurring challenge: business requirements arrive as lengthy English documents describing complex data transformations, but translating these requirements into production code is time-consuming, error-prone, and ambiguous. How do you ensure that the code you write actually implements what the business asked for?

Traditional approaches struggle with this disconnect:
- Business requirements written in prose leave room for interpretation
- Manual translation to code introduces errors and inconsistencies
- Multiple data platforms (DBT, Dataform, PySpark) require different implementations
- Testing and validation happen too late in the development cycle

## A New Approach: The Spec-Driven Pipeline

What if we could introduce an intermediate layer between business requirements and code - a structured, machine-readable specification that eliminates ambiguity and enables automated code generation?

This is the core idea behind the **spec-driven pipeline approach**:

```
Business Requirements (English)
          ↓
    [LLM Conversion]
          ↓
Technical Specification (JSON)
          ↓
    [LLM Generation - Parallel Tracks]
          ↓
    ┌──────────────────────────────────────────────────────┐
    │                         │                            │
    ↓                         ↓                            ↓
Platform-Specific Code   Test Specifications   Visual Documentation
(DBT/Dataform/PySpark)  (Assertions/Fixtures)  (Mermaid/Diagrams)
    │                         │                            │
    └──────────────────────────────────────────────────────┘
          ↓
    [Automated Testing]
          ↓
    [Human Review & Validation]
    (Reviews visual diagrams + test results)
          ↓
Production Pipeline
```

## The Multi-Stage Process

### Stage 1: Business Requirements

Let's start with a typical business requirement. Here's a real example:

```markdown
## Model: stg_customers (schema: temp)
Sources: raw.crm_customers, raw.crm_addresses

Column mapping:
| target_column   | from_table    | from_column | transform                    |
|-----------------|---------------|-------------|------------------------------|
| customer_id     | crm_customers | customer_id |                              |
| email           | crm_customers | email       | LOWER(TRIM({from}))          |
| phone_e164      | crm_customers | phone       | [complex phone normalization]|
| lifecycle_stage | crm_customers | status      | [case statement mapping]     |
| country         | crm_addresses | country     |                              |

Joins:
| left_table    | right_table   | type | condition                                    |
|---------------|---------------|------|----------------------------------------------|
| crm_customers | crm_addresses | LEFT | crm_customers.customer_id = crm_addresses... |

Filters:
| applies_to    | predicate           | rationale                |
|---------------|---------------------|--------------------------|
| crm_addresses | country IS NOT NULL | drop incomplete addresses|
```

This is a structured business requirement, but it's still in markdown format designed for humans. An LLM can read this, but it requires interpretation.

### Stage 2: Technical Specification (JSON)

The first LLM step converts the business requirement into an unambiguous JSON specification:

```json
{
  "name": "stg_customers",
  "layer": "staging",
  "sources": ["raw.crm_customers", "raw.crm_addresses"],
  "column_mapping": [
    {
      "target_column": "customer_id",
      "type": "INT64",
      "from_table": "crm_customers",
      "from_column": "customer_id",
      "transform": null,
      "nullable": false,
      "tests": ["not_null", "unique"],
      "description": "Primary business key"
    },
    {
      "target_column": "email",
      "type": "STRING",
      "from_table": "crm_customers",
      "from_column": "email",
      "transform": "LOWER(TRIM({from}))",
      "nullable": false,
      "tests": ["not_null"],
      "description": "Standardized email"
    }
  ],
  "joins": [
    {
      "left_table": "crm_customers",
      "right_table": "crm_addresses",
      "type": "LEFT",
      "condition": "crm_customers.customer_id = crm_addresses.customer_id"
    }
  ],
  "filters": [
    {
      "applies_to": "crm_addresses",
      "predicate": "country IS NOT NULL",
      "rationale": "drop incomplete addresses"
    }
  ],
  "constraints": {
    "primary_key": "customer_id"
  }
}
```

**Why is this powerful?**
- Every column mapping is explicit (source table, source column, target column, transformation)
- Data types are declared unambiguously
- Join conditions are precisely specified
- Tests and constraints are machine-readable
- No room for interpretation or guesswork

**The Challenge: JSON is Not Human-Friendly**

While JSON is perfect for machines, it becomes difficult for humans to review when specs grow large. A 500-line JSON file with nested structures is hard to scan and validate.

**The Solution: Deterministic Visual Representations**

Here's a critical insight: **Don't use LLMs to generate visualizations from the JSON spec.** That introduces unnecessary risk of errors and inconsistencies.

Instead, use **deterministic, programmatic generation** (e.g., Python scripts) to convert the structured JSON into human-readable formats. Since JSON is structured data, this conversion should be:
- **Deterministic**: Same JSON always produces the same diagram
- **Reliable**: No hallucination or interpretation errors
- **Fast**: Instant generation without LLM calls
- **Verifiable**: Logic is in code, not in prompts

For example, a simple Python script can read the JSON spec and generate a Mermaid diagram:

```mermaid
graph LR
    subgraph Sources
        A[raw.crm_customers]
        B[raw.crm_addresses]
    end

    subgraph Transformations
        C[Filter: country IS NOT NULL]
        D[Transform: LOWER TRIM email]
        E[Transform: Normalize phone to E.164]
        F[Transform: Map status to lifecycle_stage]
    end

    subgraph Target
        G[temp.stg_customers]
    end

    A -->|customer_id, email, phone, status| D
    A -->|customer_id, email, phone, status| E
    A -->|customer_id, email, phone, status| F
    B -->|country, city, state, postal_code| C
    C -->|LEFT JOIN on customer_id| G
    D --> G
    E --> G
    F --> G

    style G fill:#90EE90
    style A fill:#87CEEB
    style B fill:#87CEEB
```

Or a simplified table view:

```markdown
## Pipeline: stg_customers

**Sources:** raw.crm_customers ⟵ LEFT JOIN ⟵ raw.crm_addresses

**Transformations:**
- email → LOWER(TRIM(email))
- phone → E.164 format
- status → lifecycle_stage mapping
- Filter addresses: country IS NOT NULL

**Output:** temp.stg_customers
**Primary Key:** customer_id
**Tests:** NOT NULL, UNIQUE on customer_id
```

**Benefits for Human Review:**
- **At-a-glance understanding** of data flow
- **Easy identification** of transformation logic
- **Quick validation** of join relationships
- **Accessible to non-technical stakeholders** (business users, analysts)
- **Better for documentation** and onboarding

**The Workflow:**
```
JSON Spec (machine-readable, source of truth)
    ↓
    ├─→ [LLM] Generate Platform Code (DBT/Dataform/PySpark)
    ├─→ [LLM or Script] Generate Tests (validation logic)
    └─→ [Python Script] Generate Diagrams (Mermaid/Tables)
                        └─→ Deterministic, no LLM
```

**Critical Distinction:**
- **Code generation**: Uses LLMs (requires interpretation of spec into platform-specific syntax)
- **Test generation**: Can use LLMs or deterministic scripts
- **Diagram generation**: Should use deterministic Python scripts (no LLMs)

**Why this matters:**
- **JSON is the source of truth** - it's stored in version control, reviewed, and approved
- **Diagrams and tables are for human convenience** - they help reviewers quickly understand the spec
- **Diagrams must be perfectly consistent** with JSON - any discrepancy creates confusion
- **Using deterministic scripts** ensures diagram always matches the JSON exactly
- **No hallucination risk** - Python can't misinterpret or creatively alter the spec

This way:
- **Machines** execute from the precise JSON
- **Humans** review using the clear visualizations (generated deterministically from JSON)
- **Perfect consistency** between what humans see and what machines execute

### Stage 3: Code Generation

With the JSON spec in hand, an LLM can now generate platform-specific code with high accuracy. Here's the generated Dataform code:

```sql
config({
  type: "table",
  schema: "temp"
})
WITH
  crm_customers AS (
    SELECT
      customer_id,
      email,
      phone,
      status,
      created_at
    FROM
      `${ref('raw.crm_customers')}`
  ),
  crm_addresses AS (
    SELECT
      customer_id,
      country,
      city,
      state,
      postal_code
    FROM
      `${ref('raw.crm_addresses')}`
    WHERE
      country IS NOT NULL  -- Filter from spec
  ),
  joined AS (
    SELECT
      crm_customers.customer_id AS customer_id,
      LOWER(TRIM(crm_customers.email)) AS email,  -- Transform from spec
      CASE
        WHEN REGEXP_CONTAINS(REGEXP_REPLACE(crm_customers.phone, '[^0-9]', ''), r'^1?[0-9]{10}$')
          THEN CONCAT('+1', RIGHT(REGEXP_REPLACE(crm_customers.phone, '[^0-9]', ''), 10))
        WHEN REGEXP_CONTAINS(REGEXP_REPLACE(crm_customers.phone, '[^0-9]', ''), r'^[0-9]{11,15}$')
          THEN CONCAT('+', REGEXP_REPLACE(crm_customers.phone, '[^0-9]', ''))
        ELSE NULL
      END AS phone_e164,
      crm_addresses.country AS country,
      crm_addresses.city AS city,
      crm_customers.created_at AS created_at
    FROM
      crm_customers
      LEFT JOIN crm_addresses ON crm_customers.customer_id = crm_addresses.customer_id
  )
SELECT * FROM joined
```

The LLM follows the specification exactly:
- CTEs for each source table
- Filters applied where specified
- Joins configured per the spec
- Transformations applied to the correct columns
- Column aliases matching target names

### Stage 3b: Parallel Test Generation

At the same time the pipeline code is being generated, the LLM can also generate comprehensive test specifications. This happens in parallel, using the same JSON spec as the source of truth.

The test generation can be done:
1. **Using LLMs** to create test cases based on the specification
2. **Programmatically** by parsing the JSON spec and generating standard test patterns

Here's an example of LLM-generated test specifications:

```python
# Test specification for stg_customers
test_cases = [
    {
        "name": "test_customer_id_uniqueness",
        "type": "assertion",
        "query": """
            SELECT customer_id, COUNT(*) as cnt
            FROM stg_customers
            GROUP BY customer_id
            HAVING cnt > 1
        """,
        "expected_rows": 0,
        "description": "Ensure customer_id is unique"
    },
    {
        "name": "test_email_lowercased",
        "type": "transformation",
        "input_data": {
            "crm_customers": [
                {"customer_id": 1, "email": "TEST@EXAMPLE.COM", "status": "active"}
            ]
        },
        "expected_output": [
            {"customer_id": 1, "email": "test@example.com"}
        ],
        "description": "Verify email is lowercased"
    },
    {
        "name": "test_filter_null_countries",
        "type": "row_count",
        "query": """
            SELECT COUNT(*)
            FROM stg_customers
            WHERE country IS NULL
        """,
        "expected": "based on join with filtered addresses",
        "description": "Addresses with null countries should be filtered out"
    }
]
```

**Benefits of parallel test generation:**
- Tests are derived directly from the spec (same source of truth)
- Coverage is comprehensive and systematic
- Tests can run locally before cloud deployment
- Both positive and negative test cases can be generated
- Edge cases from the spec (nullable fields, transformations) are automatically covered

### Stage 4: Automated Testing

Once both the pipeline code and test specifications are generated, automated testing validates:
- **Schema tests**: Column names, types, nullability match the spec
- **Transformation tests**: Business logic is correctly implemented
- **Data quality tests**: Constraints and business rules are enforced
- **Integration tests**: Joins and filters work as expected

This can happen:
- **Locally** using BigQuery emulators or in-memory databases
- **In a dev environment** with synthetic data
- **In staging** with production-like data

### Stage 5: Human Review & Validation

**This is a critical, non-negotiable step.** Despite the automation, human engineers must review and validate:

**What to Review:**
1. **Spec Accuracy**: Does the JSON spec truly represent the business requirement?
2. **Code Quality**: Is the generated code performant, idiomatic, and maintainable?
3. **Test Coverage**: Are edge cases and business logic properly tested?
4. **Data Quality**: Do the results make business sense?
5. **Security & Compliance**: Are PII handling and access controls correct?

**Who Reviews:**
- Data engineers who understand the platform and performance implications
- Business stakeholders who can validate the logic matches requirements
- Data governance teams for compliance and security

**Review Criteria:**
```markdown
✓ Spec matches business requirements
✓ Generated code follows platform best practices
✓ All tests pass (unit, integration, data quality)
✓ Performance is acceptable (query cost, execution time)
✓ No security or compliance issues
✓ Documentation is clear and complete
✓ Edge cases are handled appropriately
```

Only after human approval should the pipeline be promoted to production.

## The Benefits of This Approach

### 1. Eliminating Ambiguity

The JSON spec serves as a "contract" between business and engineering. There's no ambiguity about:
- Which columns map to which targets
- What transformations are applied
- How tables are joined
- What tests should be run

### 2. Multi-Platform Support

The same JSON spec can generate code for different platforms:
- **Dataform** (BigQuery)
- **DBT** (Snowflake, Redshift, etc.)
- **PySpark** (Databricks, EMR)
- **Native SQL** (any database)

This means you can:
- Migrate between platforms more easily
- Support hybrid cloud architectures
- Generate proof-of-concept code in multiple platforms

### 3. Testability and Validation

With structured specs, you can:
- Auto-generate test cases based on the `tests` field
- Validate that generated code matches the spec
- Run tests locally using BigQuery emulators before deployment
- Shift testing left in the development cycle

### 4. Version Control and Change Management

JSON specs are:
- Easy to diff in version control
- Machine-readable for automated validation
- Queryable for impact analysis
- Suitable for automated documentation generation

### 5. Reduced Development Time

Once you have a well-engineered prompt and schema context:
- Code generation is near-instantaneous
- Tests are auto-generated
- Documentation writes itself
- Changes to requirements are reflected quickly

## Critical Success Factors

### 1. Schema Knowledge

The LLM needs complete knowledge of source table schemas. Provide:
- Table DDL definitions
- Column data types
- Relationships and constraints
- Sample data (if possible)

Without this context, the LLM will make assumptions or errors.

### 2. Prompt Engineering

The quality of generated specs and code depends heavily on:
- Clear, structured prompts
- Examples of good specs
- Platform-specific code patterns
- Error handling requirements

This is not trivial work - it requires expertise and iteration.

### 3. Validation Layer

You must validate:
- That the JSON spec accurately represents business requirements
- That generated code correctly implements the spec
- That tests cover edge cases
- That performance characteristics are acceptable

### 4. Human Review

LLM-generated code should be reviewed by engineers who understand:
- The business context
- The platform specifics
- Performance implications
- Data quality requirements

## What This Approach Enables

### Fast Iteration

When business requirements change:
1. Update the markdown requirement
2. Regenerate the JSON spec
3. Regenerate the code and test specifications (in parallel)
4. Run automated tests
5. **Human review and validation**
6. Deploy to production

While the generation steps (1-4) can happen in minutes, the human review is essential and prevents rushing flawed code to production. However, this is still dramatically faster than traditional manual development.

### Consistency

All pipelines follow the same patterns:
- Consistent naming conventions
- Standard error handling
- Uniform test coverage
- Predictable structure

### Knowledge Transfer

New team members can:
- Read the JSON spec to understand pipelines
- See the exact mapping from requirements to code
- Generate similar pipelines following established patterns

### Platform Migration

Moving from DBT to Dataform, or from SQL to PySpark, becomes:
- A matter of regenerating code from the same spec
- Automated rather than manual
- Lower risk with automated testing

## Questions This Raises

This approach opens up important questions we'll explore in future posts:

1. **How do we ensure LLM-generated code is production-quality?**
   - What validation checks are needed?
   - How do we handle edge cases?
   - What about performance optimization?

2. **How do we test locally before deploying to production?**
   - BigQuery emulators vs. cloud sandboxes
   - Test data generation strategies
   - Integration testing approaches

3. **What's the role of prompt engineering?**
   - How much expertise is required?
   - How do we version and test prompts?
   - Platform-specific considerations

4. **How do we handle complex transformations?**
   - Window functions
   - Recursive CTEs
   - Advanced analytics functions

5. **What about governance and compliance?**
   - Who reviews the specs?
   - How do we ensure data quality?
   - What about PII and security?

## The Shift in Engineering Skills: From Code Writers to Code Reviewers

**A Critical Point: Engineers Are More Important, Not Less**

With LLMs generating code automatically, you might think engineers have less work to do. **This is fundamentally wrong.**

The reality is that engineers become **more crucial** and face **more challenging** responsibilities:

### What Changes

**Before (Manual Development):**
- Engineers write SQL/Python syntax by hand
- Time spent on code syntax and debugging syntax errors
- Focus on translating requirements into working code
- Testing happens after code is written

**After (LLM-Generated Code):**
- Engineers **review** LLM-generated code for correctness
- Time spent on validating logic and identifying subtle flaws
- Focus on ensuring code meets business requirements and quality standards
- Testing strategy must be designed upfront to validate rapidly-changing code

### The New Engineering Skillset

Engineers need to develop **advanced skills** in:

1. **Code Review at Scale**
   - Quickly identifying logical errors in generated code
   - Spotting performance issues (inefficient joins, missing indexes, etc.)
   - Recognizing security vulnerabilities (SQL injection, data exposure)
   - Understanding generated code patterns across multiple platforms

2. **Test Strategy Design**
   - Creating comprehensive test suites that can validate any generated code
   - Designing tests that catch edge cases and business logic errors
   - Building test frameworks that run quickly for rapid iteration
   - Ensuring tests remain valid as code changes frequently

3. **Specification Design**
   - Writing precise, unambiguous specifications
   - Understanding what can and cannot be expressed in the spec format
   - Anticipating how specs will translate to code
   - Designing specs that are maintainable and evolvable

4. **Quality Assurance**
   - Validating that generated code meets performance requirements
   - Ensuring generated code follows platform best practices
   - Verifying data quality and correctness at scale
   - Tuning and optimizing generated code when needed

### The Testing Challenge

**This is perhaps the most critical challenge:**

Since code generation is now **fast and frequent**, the ability to quickly validate that code is correct becomes **mission-critical**.

Traditional testing approaches don't work well here:
- ❌ Manual testing is too slow for rapid iteration
- �� Writing tests after code generation defeats the purpose
- ❌ Point-in-time tests may not catch regressions

**What's needed:**
- ✅ Test specifications generated alongside code (from the same spec)
- ✅ Automated test execution (local or CI/CD)
- ✅ Comprehensive coverage (schema, logic, data quality, performance)
- ✅ Fast feedback loops (seconds to minutes, not hours)

**Example Scenario:**

Business requirement changes slightly → JSON spec updated → Code regenerated in 30 seconds

**But can you validate it's correct in 30 seconds?**

If not, you have a bottleneck. The engineer must:
- Quickly review the visual diagram to understand changes
- Review the generated code for any obvious issues
- Run automated tests to validate correctness
- Check performance characteristics
- Approve or reject the change

This requires **higher-level thinking** than writing SQL syntax:
- Understanding business logic deeply
- Knowing what tests are needed
- Recognizing patterns of errors
- Making judgment calls on trade-offs

### Why Engineers Become More Valuable

With LLM-generated code:
- **Quality control** becomes paramount (catching flaws in generated code)
- **Architecture decisions** matter more (specs define the system)
- **Testing strategy** is critical (validating frequent changes)
- **Performance tuning** requires expertise (optimizing generated code)
- **Security review** is essential (LLMs can introduce vulnerabilities)

These are **higher-value activities** than writing boilerplate SQL.

### The Bottom Line

**LLMs shift engineers from:**
- Writing repetitive code → Reviewing and validating generated code
- Debugging syntax errors → Ensuring correctness and quality
- Manual testing → Designing comprehensive test strategies
- Line-by-line development → System-level architecture and design

**This is more challenging, not less.**

Engineers who master these skills will be invaluable. Those who can:
- Design clear specifications
- Build robust testing frameworks
- Quickly identify issues in generated code
- Optimize for performance and quality
- Ensure security and compliance

...will be the ones driving successful LLM-assisted development.

## Getting Started

The spec-driven pipeline approach represents a fundamental shift in how we think about data engineering:

**From:** Manual translation of ambiguous requirements into code
**To:** Automated generation from structured, machine-readable specifications

**From:** Engineers as code writers
**To:** Engineers as architects, reviewers, and quality assurance experts

The key insight is that **the specification is the source of truth**, not the code. Code becomes a generated artifact that can be regenerated for different platforms or updated when requirements change.

This approach doesn't eliminate the need for skilled data engineers. Instead, it **elevates** their role to focus on:
- Designing robust specifications and architectures
- Building comprehensive testing and validation frameworks
- Ensuring code quality, performance, and security
- Making critical judgment calls on trade-offs and optimizations

The LLM handles the repetitive, error-prone work of translating specs into code. **Engineers handle everything that requires judgment, expertise, and deep understanding.**

## What's Next

This post introduces the spec-driven pipeline concept and workflow. However, we've intentionally left many important questions unanswered:

**Testing & Validation Challenges:**
- How do we design test strategies that can keep pace with rapid code generation?
- What tools and frameworks work best for local testing (BigQuery emulators, etc.)?
- How do we ensure comprehensive test coverage without slowing down development?
- What patterns work for testing complex transformations and edge cases?

**Code Quality & Review:**
- How do engineers effectively review LLM-generated code at scale?
- What are common patterns of errors in LLM-generated SQL/Python?
- How do we tune and optimize generated code for performance?
- What quality gates and checks should be automated?

**Engineering Skills & Practices:**
- What specific skills do engineers need to develop for this new workflow?
- How do we train teams to shift from writing code to reviewing and validating it?
- What does a mature spec-driven development process look like?
- How do we balance speed with quality in LLM-assisted development?

We're not trying to solve all these challenges in this introductory post. These are deep topics that deserve dedicated exploration.

**In upcoming posts, we'll dive deeper into:**
- Detailed prompt engineering strategies for spec and code generation
- Local testing strategies with BigQuery emulators and synthetic data
- Code review best practices for LLM-generated pipelines
- Building robust test frameworks that enable rapid validation
- Handling complex transformations (window functions, recursive CTEs, etc.)
- Production deployment and monitoring patterns
- Real-world case studies and lessons learned
- Building a library of reusable spec patterns and testing templates

**The key message:** The spec-driven approach is powerful, but success requires engineers to develop new skills in specification design, testing strategy, and code review. The challenges are real, but so are the opportunities.

The future of data engineering may not be in writing SQL by hand, but in crafting precise specifications, designing comprehensive test strategies, and ensuring the quality of AI-generated code.

---

**About This Project**

This blog post is based on the [Spec-Driven Pipeline](https://github.com/agentic/agentic_spec_driven_pipeline) open-source project, which demonstrates the complete workflow from business requirements to tested, production-ready code.

Explore the repo to see:
- Real business requirement examples
- JSON specification schemas
- Generated code for multiple platforms
- Testing strategies and examples