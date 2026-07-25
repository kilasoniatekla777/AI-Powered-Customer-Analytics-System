import os
import json
import pandas as pd
import joblib
from dotenv import load_dotenv

# Absolute imports from backend module
from backend.db import engine

# Import LLM SDKs
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# Load environment variables
load_dotenv()

# Select LLM Provider (default to openai)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()


def load_cluster_data():
    """
    Attempts to load cluster data. First tries to read from the generated CSV.
    Falls back to running predictions using the database and saved KMeans model if CSV is missing.
    """
    csv_path = "data/customer_segments.csv"
    
    if os.path.exists(csv_path):
        print(f"Loading cluster data from existing CSV: {csv_path}")
        return pd.read_csv(csv_path)
    
    print("CSV not found. Falling back to database + K-Means model prediction...")
    
    # Query database
    query = "SELECT * FROM customer_features;"
    df = pd.read_sql(query, engine)
    
    # Prepare features identically to original visualization
    features = [
        "number_of_orders",
        "total_spent",
        "average_review_score",
        "recency_days"
    ]
    
    X = df[features].copy()
    X = X.fillna({
        "number_of_orders": 0,
        "total_spent": 0,
        "average_review_score": X["average_review_score"].mean(),
        "recency_days": X["recency_days"].mean()
    })
    
    # Load scaling and clustering components
    # (Using StandardScaler to align with training steps)
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model_path = "models/customer_segmentation.pkl"
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Neither the segments CSV ({csv_path}) nor the trained model ({model_path}) exists. "
            "Please run 'python -m ml.customer_segmentation' first."
        )
        
    model = joblib.load(model_path)
    df["customer_cluster"] = model.predict(X_scaled)
    
    return df


def generate_llm_insight(prompt: str) -> str:
    """
    Dispatches the prompt to either OpenAI or Anthropic API based on configurations.
    Uses default client setups which retrieve API keys automatically from the environment.
    """
    if LLM_PROVIDER == "anthropic":
        if not HAS_ANTHROPIC:
            raise ImportError("Anthropic package is not installed.")
        
        print("Calling Anthropic API (Claude)...")
        client = Anthropic()
        # Using claude-3-5-sonnet-latest as requested
        response = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=800,
            system="You are a senior customer analytics and marketing strategy consultant.",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response.content[0].text.strip()
        
    else:  # Default to OpenAI
        if not HAS_OPENAI:
            raise ImportError("OpenAI package is not installed.")
            
        print("Calling OpenAI API (GPT)...")
        client = OpenAI()
        # Using gpt-4o-mini for cost-efficiency and speed
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a senior customer analytics and marketing strategy consultant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.2
        )
        return response.choices[0].message.content.strip()


def parse_response(insight_text: str):
    """
    Helper function to parse the LLM's response into Description and Recommendation fields.
    """
    description = ""
    recommendation = ""
    
    lines = insight_text.split("\n")
    current_section = None
    
    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue
            
        if cleaned.lower().startswith("description:"):
            current_section = "desc"
            description = cleaned[len("description:"):].strip()
        elif cleaned.lower().startswith("recommendation:"):
            current_section = "rec"
            recommendation = cleaned[len("recommendation:"):].strip()
        else:
            if current_section == "desc":
                description += " " + cleaned
            elif current_section == "rec":
                recommendation += " " + cleaned
                
    return description.strip(), recommendation.strip()


def main():
    try:
        df = load_cluster_data()
    except Exception as e:
        print(f"Error loading cluster data: {e}")
        return

    features = ["number_of_orders", "total_spent", "average_review_score", "recency_days"]
    
    # Calculate profiles per cluster
    profiles = df.groupby("customer_cluster")[features].mean().reset_index()
    print(f"\nCalculated profiles for {len(profiles)} clusters.")
    
    insights = []
    
    for _, row in profiles.iterrows():
        cluster_id = int(row["customer_cluster"])
        orders = float(row["number_of_orders"])
        spent = float(row["total_spent"])
        review = float(row["average_review_score"])
        recency = float(row["recency_days"])
        
        print(f"\n--- Processing Cluster {cluster_id} ---")
        print(f"Stats - Orders: {orders:.2f}, Spent: ${spent:.2f}, Review: {review:.2f}, Recency: {recency:.1f} days")
        
        prompt = (
            f"Analyze this customer segment from our e-commerce database with the following average metrics:\n"
            f"- Average Number of Orders: {orders:.2f}\n"
            f"- Average Total Spent: ${spent:.2f}\n"
            f"- Average Customer Review Score: {review:.2f} out of 5.0\n"
            f"- Average Recency (Days since last purchase): {recency:.1f} days\n\n"
            f"Format your response exactly as follows:\n"
            f"Description: <Provide a short, plain-language description summarizing who these customers are, "
            f"their value, and their loyalty status in 2-3 sentences.>\n"
            f"Recommendation: <Provide one concrete, highly actionable marketing or operational business "
            f"recommendation to target, upsell, retain, or win-back this segment.>"
        )
        
        try:
            raw_insight = generate_llm_insight(prompt)
            desc, rec = parse_response(raw_insight)
            
            # Fallback parsing in case the LLM formatting is slightly off
            if not desc or not rec:
                desc = raw_insight
                rec = "Refer to the raw insight description."
                
            insights.append({
                "cluster": cluster_id,
                "metrics": {
                    "number_of_orders": orders,
                    "total_spent": spent,
                    "average_review_score": review,
                    "recency_days": recency
                },
                "raw_insight": raw_insight,
                "parsed_insight": {
                    "description": desc,
                    "recommendation": rec
                }
            })
            
            # Print to stdout
            print(f"AI-Generated Explanation:")
            print(f"  Description: {desc}")
            print(f"  Recommendation: {rec}")
            
        except Exception as e:
            print(f"Error generating insight for cluster {cluster_id}: {e}")
            insights.append({
                "cluster": cluster_id,
                "metrics": {
                    "number_of_orders": orders,
                    "total_spent": spent,
                    "average_review_score": review,
                    "recency_days": recency
                },
                "error": str(e)
            })

    # Save to JSON
    json_path = "data/cluster_insights.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(insights, f, indent=4, ensure_ascii=False)
    print(f"\nSaved insights to JSON: {json_path}")
    
    # Save to Markdown
    md_path = "data/cluster_insights.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# 🤖 AI-Generated Customer Segment Insights\n\n")
        f.write("This file contains the AI-generated profiles and action recommendations for each customer segment.\n\n")
        
        for ins in insights:
            cluster_id = ins["cluster"]
            metrics = ins["metrics"]
            
            f.write(f"## 👥 Segment Cluster {cluster_id}\n\n")
            f.write("### 📊 Metrics Profile\n")
            f.write(f"- **Average Number of Orders**: {metrics['number_of_orders']:.2f}\n")
            f.write(f"- **Average Total Spent**: ${metrics['total_spent']:.2f}\n")
            f.write(f"- **Average Review Score**: {metrics['average_review_score']:.2f} / 5.0\n")
            f.write(f"- **Average Recency**: {metrics['recency_days']:.1f} days\n\n")
            
            if "error" in ins:
                f.write(f"> ❌ **Error generating insights**: {ins['error']}\n\n")
            else:
                parsed = ins["parsed_insight"]
                f.write("### 📝 Profile Description\n")
                f.write(f"{parsed['description']}\n\n")
                f.write("### 💡 Business Recommendation\n")
                f.write(f"> **Action Plan**: {parsed['recommendation']}\n\n")
            f.write("---\n\n")
            
    print(f"Saved insights to Markdown: {md_path}")


if __name__ == "__main__":
    main()
