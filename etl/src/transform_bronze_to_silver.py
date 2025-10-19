from pathlib import Path
from pendulum import today
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transform_brewery_bronze_to_silver():

    execution_date = os.getenv("EXECUTION_DATE")
    data_root = os.getenv("DATA_OUTPUT_ROOT", "/app/data")
    bronze_path = Path(data_root) / f"medallion/bronze/breweries/{execution_date}"
    silver_path = Path(data_root) / f"medallion/silver/breweries/{execution_date}"
    silver_path.mkdir(parents=True, exist_ok=True)

    spark = SparkSession.builder \
        .appName("Brewery-Transformation") \
        .master("local[*]") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.parquet.compression.codec", "snappy") \
        .getOrCreate()
    
    try:
        df_bronze = spark.read.option("multiline", "true").json(str(bronze_path))

        df_silver = (
            df_bronze.dropDuplicates()
            .filter(
                col("brewery_type").isNotNull() &
                col("state").isNotNull() &
                col("country").isNotNull())
            .select(
                col("id").cast("string"),
                col("name").cast("string"),
                col("brewery_type").cast("string"),
                col("street").cast("string"),
                col("city").cast("string"),
                col("state").cast("string"),
                col("postal_code").cast("string"),
                col("country").cast("string"),
                col("longitude").cast("double"),
                col("latitude").cast("double"),
                col("phone").cast("string"),
                col("website_url").cast("string"),
                current_timestamp().alias("processed_at")
            )
        )

        df_silver.coalesce(1) \
            .write \
            .mode("overwrite") \
            .option("compression", "snappy") \
            .partitionBy("country","state") \
            .parquet(str(silver_path))

        logging.info(f"Saved records in: {silver_path}")
        logging.info(f"Total records in Silver layer: {df_silver.count()}")
        logging.info(df_silver.show(10, truncate=False))

    finally:
        spark.stop()

def main():
    transform_brewery_bronze_to_silver()

if __name__ == "__main__":
    main()
