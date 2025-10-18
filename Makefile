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
	kubectl apply -f $(K8S_DIR)/airflow-role-binding.yaml

start-airflow:
	cd $(AIRFLOW_DIR) && docker-compose up -d

copy-dags: start-airflow
	docker cp $(AIRFLOW_DIR)/dags/brewery_pipeline.py airflow-airflow-webserver-1:/opt/airflow/dags/

test:
	cd $(TESTS_DIR) && python3 -m pytest

status:
	@echo ">>> Kubernetes Pods:"
	kubectl get pods -n default

help:
	@echo "Comandos disponíveis:"
	@echo "  make all             - Setup completo (build, infra, Airflow, DAGs)"
	@echo "  make build-image     - Reconstrói a imagem do pipeline"
	@echo "  make apply-k8s       - Aplica PV/PVC/RBAC no cluster Kubernetes"
	@echo "  make start-airflow   - Inicia Airflow, Postgres, Grafana"
	@echo "  make copy-dags       - Atualiza DAG no Airflow"
	@echo "  make test            - Executa testes unitários"
	@echo "  make status          - Mostra status do cluster e containers"
	@echo "  make clean           - Para tudo e remove dados persistentes"