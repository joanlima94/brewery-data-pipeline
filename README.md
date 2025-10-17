# Brewery DB Data Pipeline

This project implements a **medallion architecture** (Bronze → Silver → Gold) to ingest, transform, and serve data from the [Open Brewery DB API](https://www.openbrewerydb.org/documentation). The pipeline is orchestrated with **Apache Airflow**, containerized with **Docker**, deployable on **Kubernetes**, and monitored via **Grafana**.

---

## 🌐 Data Source

- **API**: `https://api.openbrewerydb.org/v1/breweries`
- **Metadata endpoint**: `https://api.openbrewerydb.org/v1/breweries/meta`
- **Pagination**: Up to 200 records per page
- **Total records**: ~10,000 breweries (as of 2025)

---

## 🏗️ Architecture Overview




### Layers

- **Bronze**: Raw JSON responses from the API, partitioned by ingestion date.
- **Silver**: Cleaned, deduplicated, strongly-typed Parquet files with schema enforcement and a `processed_at` timestamp.
- **Gold**: (Future) Business-ready aggregations (e.g., count by state, brewery type distribution).

---

## 🧪 Key Features

- ✅ **Idempotent daily ingestion** (partitioned by date)
- ✅ **Resilient API client** with retry logic for `429 Too Many Requests`
- ✅ **PySpark-based transformation** (scalable, schema-on-read + schema enforcement)
- ✅ **Snappy-compressed Parquet** output for efficient storage and query performance
- ✅ **Unit tests** for ingestion and transformation logic
- ✅ **Airflow DAG** using `KubernetesPodOperator` for task isolation
- ✅ **Monitoring-ready**: Logs structured for Grafana/Loki; metrics can be exported to Prometheus

---

## 📦 Project Structure


```bash
openbrewerydb-data-pipeline/
├── ingestion/                   # API extraction logic
│   ├── src/
│   │   └── extract.py           # Fetches paginated JSON from Open Brewery DB
│   └── tests/
├── medallion/
│   ├── bronze/                  # Raw data (written by ingestion)
│   ├── silver/                  # Cleaned data (PySpark job)
│   │   └── process.py
│   └── gold/                    # (TBD) Aggregated views
├── runner.py                    # Entry point for local/container execution
├── requirements.txt             # Python dependencies (requests, pyspark)
├── Dockerfile                   # Builds container with Java 21 + PySpark
└── README.md