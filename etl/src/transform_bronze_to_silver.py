from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp
from datetime import datetime
from zoneinfo import ZoneInfo
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transform_brewery_bronze_to_silver():

    today = datetime.now(ZoneInfo('America/Sao_Paulo')).date()
    bronze_path = f"{Path().absolute()}/medallion/bronze/breweries/{str(today)}"
    silver_path = f"{Path().absolute()}/medallion/silver/breweries/{str(today)}"

    spark = SparkSession.builder \
        .appName("Brewery-Transformation") \
        .master("local[*]") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.parquet.compression.codec", "snappy") \
        .getOrCreate()
    
    try:
        df_bronze = spark.read.option("multiline", "true").json(bronze_path)

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
            .parquet(silver_path)

        logging.info(f"Saved records in: {silver_path}")
        logging.info(f"Total records in Silver layer: {df_silver.count()}")
        logging.info(df_silver.show(10, truncate=False))

    finally:
        spark.stop()

def main():
    transform_brewery_bronze_to_silver()

if __name__ == "__main__":
    main()
