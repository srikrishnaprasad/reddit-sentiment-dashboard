import json
import psycopg2
import boto3
import os
from collections import defaultdict

def lambda_handler(event, context):
    print("🚀 Lambda function started...")

    # --- Environment Variables ---
    db_host = os.environ['DB_HOST']
    db_name = os.environ['DB_NAME']
    db_user = os.environ['DB_USER']
    db_password = os.environ['DB_PASSWORD']
    bucket = "reddit-news-json-data"
    prefix = "raw_data/to_processed/"

    # --- Initialize S3 ---
    s3 = boto3.client('s3')

    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        contents = response.get('Contents', [])
        if not contents:
            raise Exception("No files found in the specified prefix.")

        # Group files by subreddit and select latest by timestamp
        latest_files = defaultdict(str)
        for obj in contents:
            key = obj['Key']
            if not key.endswith('.json'):
                continue
            filename = key.split('/')[-1]
            if '_' not in filename:
                continue
            subreddit, timestamp_part = filename.replace('.json', '').rsplit('_', 1)

            if subreddit not in latest_files or timestamp_part > latest_files[subreddit]:
                latest_files[subreddit] = timestamp_part

        files = [f"{prefix}{sub}_{ts}.json" for sub, ts in latest_files.items()]
        print(f"✅ Latest files per subreddit selected: {files}")

    except Exception as e:
        print(f"❌ Failed to list files: {e}")
        return {"statusCode": 400, "error": str(e)}

    # --- Connect to RDS ---
    try:
        conn = psycopg2.connect(
            host=db_host,
            dbname=db_name,
            user=db_user,
            password=db_password,
            port=5432
        )
        print("✅ Connected to RDS")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return {"statusCode": 500, "error": str(e)}

    cursor = conn.cursor()
    total_records = 0
    successful_files = 0

    for key in files:
        try:
            obj = s3.get_object(Bucket=bucket, Key=key)
            json_content = obj['Body'].read().decode('utf-8')
            records = json.loads(json_content)

            if not records:
                continue

            subreddit = records[0]['subreddit'].lower()
            table_name = f"reddit_sentiment_{subreddit}"

            # Create table if not exists
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    subreddit VARCHAR(50),
                    comment TEXT,
                    sentiment FLOAT,
                    sentiment_type VARCHAR(20),
                    inserted_at TIMESTAMP DEFAULT NOW()
                );
            """)
            conn.commit()

            # Truncate existing table to avoid duplicates
            cursor.execute(f"TRUNCATE TABLE {table_name};")
            conn.commit()

            # Insert new data
            insert_data = [
                (
                    r.get("subreddit"),
                    r.get("comment"),
                    r.get("sentiment"),
                    r.get("sentiment_type")
                )
                for r in records
            ]

            cursor.executemany(f"""
                INSERT INTO {table_name} (subreddit, comment, sentiment, sentiment_type)
                VALUES (%s, %s, %s, %s)
            """, insert_data)
            conn.commit()

            print(f"✅ Inserted {len(insert_data)} records into {table_name}")
            total_records += len(insert_data)
            successful_files += 1

        except Exception as e:
            print(f"⚠️ Failed to process {key}: {e}")

    cursor.close()
    conn.close()

    return {
        "statusCode": 200,
        "message": f"✅ {total_records} records inserted from {successful_files} latest files."
    }
