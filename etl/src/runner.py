import api_to_bronze
import transform_bronze_to_silver
import aggregated_silver_to_gold

if __name__ == "__main__":
    api_to_bronze.main()
    transform_bronze_to_silver.main()
    aggregated_silver_to_gold.main()