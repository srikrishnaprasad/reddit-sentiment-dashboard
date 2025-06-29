import streamlit as st
import psycopg2
import pandas as pd

# -------------------------
# RDS Config (DO NOT CHANGE)
# -------------------------
rds_host = "reddit-db-cluster.cluster-cjiika8syrhc.ap-south-1.rds.amazonaws.com"
db_name = "postgres"
db_user = "postgres"
db_password = "R3dditSecurePass!"
db_port = "5432"

# -------------------------
# DB Connection Function
# -------------------------
def get_connection():
    return psycopg2.connect(
        host=rds_host,
        dbname=db_name,
        user=db_user,
        password=db_password,
        port=db_port
    )

# -------------------------
# Topic Mapping
# -------------------------
topics = {
    "Agriculture": "agriculture",
    "Artificial Intelligence": "artificial",
    "CryptoCurrency": "cryptocurrency",
    "Data Science": "datascience",
    "Machine Learning": "machinelearning",
    "Stocks": "stocks"
}

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Reddit Sentiment Dashboard", layout="wide")
st.title("📊 Reddit Sentiment Dashboard")

selected_topic = st.selectbox("🔍 Choose a Topic:", list(topics.keys()))
table_name = f"reddit_sentiment_{topics[selected_topic]}"

# -------------------------
# Data Query and Display
# -------------------------
try:
    # Always get a fresh connection
    conn = get_connection()
    query = f"SELECT * FROM public.{table_name} ORDER BY id DESC;"
    df = pd.read_sql(query, conn)
    conn.close()  # Important to close the connection!

    # Color formatting for 'sentiment_type' column
    def color_sentiment(val):
        if val == "Positive":
            return 'background-color: #66f28d'
        elif val == "Negative":
            return 'background-color: #f35555'
        elif val == "Neutral":
            return 'background-color: #5dcef7'
        return ''

    styled_df = df.style.applymap(color_sentiment, subset=["sentiment_type"])

    # Show the table
    st.markdown("### 🧾 Sentiment Table with Colored Labels")
    st.dataframe(styled_df, use_container_width=True)

    # Show sentiment distribution chart using Streamlit's bar_chart
    st.markdown("### 📈 Sentiment Distribution")

    sentiment_counts = df['sentiment_type'].value_counts().reindex(['Positive', 'Neutral', 'Negative']).fillna(0).astype(int)
    sentiment_df = pd.DataFrame(sentiment_counts)
    sentiment_df.columns = ['Count']

    st.bar_chart(sentiment_df)

    # Debug: Show version
    st.caption(f"Running Streamlit version: {st.__version__}")

except Exception as e:
    st.error(f"❌ Failed to load data from {table_name}: {e}")
