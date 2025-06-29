# Reddit-Sentiment-Dashboard
## A Reddit-based sentiment analysis project that uses AWS Lambda for automation, TextBlob for sentiment scoring, and ECS to deploy a Streamlit dashboard that queries data from PostgreSQL RDS.
![WhatsApp Image 2025-06-24 at 12 02 20 PM](https://github.com/user-attachments/assets/50f3212d-5278-4feb-8e67-18259d726184)
### In this project 

### • We are making use of the Reddit API, accessed through the PRAW (Python Reddit API Wrapper) library, to fetch the latest comments from six  subreddits. Authentication is done using a Reddit developer account with client_id, client_secret, and user_agent.

### 1) Reddit comments are extracted with the help of a Lambda function, which is automatically triggered every 1 minute using Amazon EventBridge to ensure continuous data collection.

### •The raw data collected is analyzed for sentiment using TextBlob, and then pushed to an Amazon S3 bucket in JSON format for storage and backup.

![image](https://github.com/user-attachments/assets/99174e20-7a70-4099-899e-2b2d5755312d)

### 2) A second Lambda reads JSON and inserts into RDS PostgreSQL.

![image](https://github.com/user-attachments/assets/1fa57530-e408-4c07-acc5-1d25567200ec)


![image](https://github.com/user-attachments/assets/64a89ec9-1b00-4b5e-95e6-855c97bfea46)

### 3)  Streamlit dashboard built locally → Dockerized → Pushed to ECR.

![image](https://github.com/user-attachments/assets/77ba3914-7b16-4119-9285-6c63722f6ec2)

![image](https://github.com/user-attachments/assets/01747acd-8899-48c5-86bb-5a7a65ada99b)

### 4) ECS Fargate runs container image → Public dashboard on port 8051.

![image](https://github.com/user-attachments/assets/a9db7d71-70c3-48ca-8e8c-9486e22c09a6)

![image](https://github.com/user-attachments/assets/d463dc7d-3788-46f3-be25-ed2f75afa501)





