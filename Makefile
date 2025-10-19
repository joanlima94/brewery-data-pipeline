IMAGE_NAME = brewery-pipeline:local
AIRFLOW_DIR = orchestration/airflow
K8S_DIR = ${AIRFLOW_DIR}/k8s
SCRITPS_DIR = etl/src
TESTS_DIR = etl/tests

.PHONY: all build-image apply-k8s start-airflow copy-dags test status clean help

all: build-image apply-k8s start-airflow copy-dags

build-image:
	docker build -t $(IMAGE_NAME) .

apply-k8s:
	kubectl apply -f $(K8S_DIR)/brewery-pv-pvc.yaml
	kubectl apply -f $(K8S_DIR)/airflow-role-binding.yaml

start-airflow:
	cd $(AIRFLOW_DIR) && docker-compose up -d

copy-dags: start-airflow
	docker cp $(AIRFLOW_DIR)/dags/brewery_pipeline.py airflow-airflow-webserver-1:/opt/airflow/dags/

test:
	@echo ">>> Running tests:"
	python3 -m pytest

status:
	@echo ">>> Kubernetes Pods:"
	kubectl get pods -n default

stop:
	cd $(AIRFLOW_DIR) && docker-compose down

help:
	@echo "Comandos disponíveis:"
	@echo "  make all             - Setup all (build, infra, Airflow, DAGs)"
	@echo "  make build-image     - build Docker image"
	@echo "  make apply-k8s       - Apply PV/PVC/RBAC in Kubernetes cluster"
	@echo "  make start-airflow   - Start Airflow, Postgres, Grafana"
	@echo "  make copy-dags       - Update DAG in Airflow"
	@echo "  make test            - Run unit tests"
	@echo "  make status          - Show status of cluster and containers"
	@echo "  make stop            - Stop everything"