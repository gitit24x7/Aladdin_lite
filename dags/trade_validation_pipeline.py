"""
Aladdin Lite — Sample Trade Pipeline DAG
=========================================
This DAG represents the orchestration layer for the Aladdin platform.
It runs daily, simulating the lifecycle of a trade:
  1. Validate the trade in PostgreSQL
  2. Publish the event to Kafka
  3. Confirm the event was indexed in Elasticsearch

Think of Airflow as the "conductor" that sequences every other
service in your stack at the right time.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# --- Default DAG arguments ---
default_args = {
    "owner": "aladdin",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# --- DAG definition ---
with DAG(
    dag_id="aladdin_trade_pipeline",
    description="Orchestrates the Aladdin trade lifecycle: Postgres → Kafka → Elasticsearch",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",          # Run once per day
    catchup=False,                       # Don't backfill missed runs
    tags=["aladdin", "trades", "kafka"],
) as dag:

    # --- Task 1: Validate trade in PostgreSQL ---
    def validate_trade():
        """
        Validation rules (all must pass or the trade is REJECTED):
          - quantity must be > 0        (can't buy negative shares)
          - price must be > 0           (can't have a zero/negative price)
          - ticker must not be empty    (must identify a real asset)

        In production: connect via PostgresHook, UPDATE status='VALID' or 'REJECTED'.
        """
        trade = {
            "ticker": "TSLA",
            "quantity": 100,
            "price": 197.50,
        }

        assert trade["quantity"] > 0,  "❌ Invalid: quantity must be > 0"
        assert trade["price"]    > 0,  "❌ Invalid: price must be > 0"
        assert trade["ticker"].strip(), "❌ Invalid: ticker cannot be empty"

        print("✅ Trade validation complete — quantity, price, and ticker all passed.")

    validate = PythonOperator(
        task_id="validate_trade",
        python_callable=validate_trade,
    )

    # --- Task 2: Publish trade event to Kafka ---
    def publish_to_kafka():
        """
        In production: use the kafka-python / confluent-kafka library
        to produce a trade event to the 'trades' topic.
        """
        print("📤 Trade event published to Kafka topic: aladdin_trades")

    publish = PythonOperator(
        task_id="publish_to_kafka",
        python_callable=publish_to_kafka,
    )

    # --- Task 3: Confirm Elasticsearch indexing, we are just checking if indexed or not ---
    confirm_index = BashOperator(
        task_id="confirm_elasticsearch_index",
        bash_command="bash /opt/airflow/shell_scripts/confirm_es_index.sh ",
        # ↑ 'bash' explicitly invokes the script — avoids Linux file permission issues
        # ↑ trailing space after .sh is REQUIRED — Airflow appends a temp arg without it
    )

    # --- Pipeline dependency chain ---
    validate >> publish >> confirm_index
