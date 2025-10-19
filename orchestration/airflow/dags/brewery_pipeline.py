from datetime import datetime
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client.models import V1Volume, V1PersistentVolumeClaimVolumeSource, V1VolumeMount
from kubernetes.client import V1EnvVar

with DAG(
    "breweries-data-pipeline",
    start_date=datetime(2025, 10, 17),
    schedule="@hourly",
    catchup=False,
    tags=["brewery", "medallion"]
) as dag:

    volume = V1Volume(
        name="brewery-data",
        persistent_volume_claim=V1PersistentVolumeClaimVolumeSource(
            claim_name="brewery-data-pvc"
        )
    )
    volume_mount = V1VolumeMount(
        name="brewery-data",
        mount_path="/app/data"
    )

    extract_bronze = KubernetesPodOperator(
        task_id="acquisition_api_to_bronze",
        name="acquisition-api-to-bronze",
        namespace="default",
        image="brewery-pipeline:local",
        cmds=["python", "etl/src/api_to_bronze.py"],
        is_delete_operator_pod=True,
        log_events_on_failure=True,
        get_logs=True,
        volumes=[volume],
        volume_mounts=[volume_mount],
        env_vars=[
            V1EnvVar(name="DATA_OUTPUT_ROOT", value="/app/data")
        ],
        in_cluster=False,
        service_account_name="airflow",
        cluster_context="docker-desktop",
    )

    transform_silver = KubernetesPodOperator(
        task_id="transform_bronze_to_silver",
        name="transform-bronze-to-silver",
        namespace="default",
        image="brewery-pipeline:local",
        cmds=["python", "etl/src/transform_bronze_to_silver.py"],
        is_delete_operator_pod=True,
        log_events_on_failure=True,
        get_logs=True,
        volumes=[volume],
        volume_mounts=[volume_mount],
        env_vars=[
            V1EnvVar(name="DATA_OUTPUT_ROOT", value="/app/data")
        ],
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
        log_events_on_failure=True,
        get_logs=True,
        volumes=[volume],
        volume_mounts=[volume_mount],
        env_vars=[
            V1EnvVar(name="DATA_OUTPUT_ROOT", value="/app/data")
        ],
        in_cluster=False,
        service_account_name="airflow",
        cluster_context="docker-desktop",
    )

extract_bronze >> transform_silver >> aggregate_gold