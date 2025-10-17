from datetime import datetime
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator

with DAG(
    "breweries-data-pipeline",
    start_date=datetime(2025, 10, 17),
    schedule="@hourly",
    catchup=False,
    tags=["brewery", "medallion"]
) as dag:

    extract_bronze = KubernetesPodOperator(
        task_id="extract_bronze",
        name="acquisition-api-to-bronze",
        namespace="default",
        image="brewery-pipeline:local",
        cmds=["python", "etl/src/api_to_bronze.py"],
        is_delete_operator_pod=True,
        get_logs=True,
        volumes=[],
        volume_mounts=[],
        in_cluster=False,
        service_account_name="airflow",
        cluster_context="docker-desktop",
    )

    transform_silver = KubernetesPodOperator(
        task_id="transform_silver",
        name="transform-silver",
        namespace="default",
        image="brewery-pipeline:local",
        cmds=["python", "etl/src/transform_bronze_to_silver.py"],
        is_delete_operator_pod=True,
        get_logs=True,
        in_cluster=False,
        service_account_name="airflow",
        cluster_context="docker-desktop",
    )

    aggregate_gold = KubernetesPodOperator(
        task_id="aggregate_gold",
        name="aggregate-gold",
        namespace="default",
        image="brewery-pipeline:local",
        cmds=["python", "etl/src/aggregated_silver_to_gold.py"],
        is_delete_operator_pod=True,
        get_logs=True,
        in_cluster=False,
        service_account_name="airflow",
        cluster_context="docker-desktop",
    )

    extract_bronze >> transform_silver >> aggregate_gold