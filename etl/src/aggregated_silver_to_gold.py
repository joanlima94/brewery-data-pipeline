from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import count, current_timestamp
from datetime import datetime
from zoneinfo import ZoneInfo
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    today = datetime.now(ZoneInfo('America/Sao_Paulo')).date()
    silver_path = f"{Path().absolute()}/medallion/silver/breweries/{str(today)}"
    gold_path = f"{Path().absolute()}/medallion/gold/breweries_agg/{str(today)}"

    spark = SparkSession.builder \
        .appName("Brewery-Gold-Aggregations") \
        .master("local[*]") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()

    try:
        df_silver = spark.read.parquet(silver_path)

        aggregated_at = current_timestamp()

        agg_by_type = (
            df_silver.groupBy("brewery_type")
            .agg(count("*").alias("count_by_type"))
            .withColumn("aggregated_at", aggregated_at)
            .orderBy("count_by_type", ascending=False))
        
        agg_by_city = (
            df_silver.groupBy("city")
            .agg(count("*").alias("count_by_city"))
            .withColumn("aggregated_at", aggregated_at)
            .orderBy("count_by_city", ascending=False))
        
        agg_by_state = (
            df_silver.groupBy("state")
            .agg(count("*").alias("count_by_state"))
            .withColumn("aggregated_at", aggregated_at)
            .orderBy("count_by_state", ascending=False))
        
        agg_by_country = (
            df_silver.groupBy("country")
            .agg(count("*").alias("count_by_country"))
            .withColumn("aggregated_at", aggregated_at)
            .orderBy("count_by_country", ascending=False))

        output_base = Path(gold_path)
        output_base.mkdir(parents=True, exist_ok=True)

        agg_by_type.write.mode("overwrite").option("compression", "snappy").parquet(str(output_base / "by_brewery_type"))
        agg_by_city.write.mode("overwrite").option("compression", "snappy").parquet(str(output_base / "by_city"))
        agg_by_state.write.mode("overwrite").option("compression", "snappy").parquet(str(output_base / "by_state"))
        agg_by_country.write.mode("overwrite").option("compression", "snappy").parquet(str(output_base / "by_country"))

        logging.info(f"✅ Aggregations saved in: {gold_path}")

        logger.info("By Brewery Type:")
        agg_by_type.show()
        logger.info("By city:")
        agg_by_city.show()  
        logger.info("By state:")
        agg_by_state.show()
        logger.info("By country:")
        agg_by_country.show()

    finally:
        spark.stop()

if __name__ == "__main__":
    main()