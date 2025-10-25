
MD → spec + mappings:
python -m agentic_spec_pipeline spec-from-req --req examples/business_requirements/customer_order_pipeline_requirement.md --out-root examples/technical_requirements --use-llm
spec → Pipeline Code:
python -m agentic_spec_pipeline sqlx-from-spec --spec examples/technical_requirements/spec.json --out-dir examples/pipeline_code/definitions
spec → tests:
python -m agentic_spec_pipeline tests-from-spec --spec examples/technical_requirements/spec.json --out-dir examples/tests

Seeds (CSV): examples/seeds/*.csv
To load into BigQuery emulator (example):
# env: BIGQUERY_EMULATOR_HOST=http://127.0.0.1:9050
bq --api_endpoint=$BIGQUERY_EMULATOR_HOST mk --dataset emulator-project:raw
bq --api_endpoint=$BIGQUERY_EMULATOR_HOST mk --dataset emulator-project:temp
bq --api_endpoint=$BIGQUERY_EMULATOR_HOST mk --dataset emulator-project:analytics
bq --api_endpoint=$BIGQUERY_EMULATOR_HOST load --autodetect --source_format=CSV emulator-project:raw.crm_customers examples/seeds/crm_customers.csv
bq --api_endpoint=$BIGQUERY_EMULATOR_HOST load --autodetect --source_format=CSV emulator-project:raw.crm_addresses examples/seeds/crm_addresses.csv
bq --api_endpoint=$BIGQUERY_EMULATOR_HOST load --autodetect --source_format=CSV emulator-project:raw.commerce_orders examples/seeds/commerce_orders.csv
bq --api_endpoint=$BIGQUERY_EMULATOR_HOST load --autodetect --source_format=CSV emulator-project:raw.commerce_order_items examples/seeds/commerce_order_items.csv
bq --api_endpoint=$BIGQUERY_EMULATOR_HOST load --autodetect --source_format=CSV emulator-project:raw.support_tickets examples/seeds/support_tickets.csv
bq --api_endpoint=$BIGQUERY_EMULATOR_HOST load --autodetect --source_format=CSV emulator-project:raw.fx_rates examples/seeds/fx_rates.csv