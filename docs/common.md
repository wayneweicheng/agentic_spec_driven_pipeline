
## environment variables
.env file and env.example should be created at the project root. Please populate env.example with some sample values, and user will update the .env file accordingly.

## Source code folder structure, this is an example use this as a reference
.
├── docs
│   ├── common.md
│   └── dataform-ai-agent-testing-prd.md
├── env.example
├── examples
│   ├── requirements
│   │   ├── sample_pipeline.md
│   │   └── source_ddl
│   │       ├── commerce_order_items.sql
│   │       ├── commerce_orders.sql
│   │       ├── crm_addresses.sql
│   │       ├── crm_customers.sql
│   │       ├── fx_rates.sql
│   │       └── support_tickets.sql
│   └── sqlx_project
│       └── definitions
│           └── customer_orders.sqlx
├── README.md
├── references
│   └── repos
│       └── adk_repos.md
├── requirements.txt
├── src
│   └── agentic_spec_pipeline
│       ├── __init__.py
│       ├── __main__.py
│       ├── agent
│       │   ├── agent_runner.py
│       │   ├── config.yaml
│       │   └── requirements_agent_runner.py
│       ├── cli.py
│       ├── requirements
│       │   ├── llm_preprocessor.py
│       │   ├── parser.py
│       │   ├── sql_builder.py
│       │   ├── sqlx_generator.py
│       │   ├── table_parser.py
│       │   └── test_generator.py
│       └── tools
│           ├── mock_data.py
│           ├── sqlx_parser.py
│           └── test_generator.py
└── tests
    ├── integration_tests
    └── unit_tests