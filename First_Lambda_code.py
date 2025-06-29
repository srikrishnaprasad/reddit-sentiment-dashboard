import json
import boto3
import praw
from textblob import TextBlob
from datetime import datetime

# List of subreddits to process
SUBREDDITS = [
    "stocks",
    "CryptoCurrency",
    "MachineLearning",
    "datascience",
    "artificial",
    "agriculture"
]

def lambda_handler(event, context):
    # Initialize Reddit API
    reddit = praw.Reddit(
        client_id="ESPAj4LjxKBb8hqMaFB0yQ",
        client_secret="LFCcZRKtv6pPufbili1e7TzCHrBZRw",
        user_agent="RedditSentimentApp by /u/Srikrishnaprasad"
    )

    # Initialize S3 client
    s3 = boto3.client('s3')
    bucket_name = "reddit-news-json-data"

    # Track results for logging
    summary = []

    for subreddit_name in SUBREDDITS:
        try:
            subreddit = reddit.subreddit(subreddit_name)
            results = []

            # Fetch recent comments (limit can be adjusted)
            for comment in subreddit.comments(limit=700):
                sentiment_score = TextBlob(comment.body).sentiment.polarity
                sentiment_type = (
                    "Positive" if sentiment_score > 0 else
                    "Negative" if sentiment_score < 0 else
                    "Neutral"
                )

                results.append({
                    "subreddit": subreddit_name,
                    "comment": comment.body,
                    "sentiment": sentiment_score,
                    "sentiment_type": sentiment_type
                })

            # Save to S3 with timestamped key
            timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
            s3_key = f"raw_data/to_processed/{subreddit_name}_{timestamp}.json"

            s3.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=json.dumps(results, indent=2),
                ContentType='application/json'
            )

            summary.append(f"✅ {subreddit_name}: {len(results)} comments uploaded to {s3_key}")

        except Exception as e:
            summary.append(f"❌ {subreddit_name}: {str(e)}")

    return {
        'statusCode': 200,
        'message': "Batch sentiment fetch completed.",
        'details': summary
    }
