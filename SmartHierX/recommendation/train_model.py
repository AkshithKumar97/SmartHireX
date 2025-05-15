# train_model.py

import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
from utils import load_and_prepare_data, create_training_pairs

def train_model():
    # Load and preprocess resumes and jobs
    resumes_df, jobs_df = load_and_prepare_data("data/resumes.csv", "data/posted_jobs.csv")
    
    # Create training pairs
    pairs_df = create_training_pairs(resumes_df, jobs_df)

    # ✅ Combine resume and job text for cosine similarity-based vectorizer training
    corpus = pairs_df['resume_text'] + " " + pairs_df['job_text']
    tfidf = TfidfVectorizer(max_features=5000)
    X = tfidf.fit_transform(corpus)
    y = pairs_df['label']  # Assuming your pairs_df has a 'label' column (1 = match, 0 = no match)

    # ✅ Train Logistic Regression Model
    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)

    # ✅ Save trained model and vectorizer
    os.makedirs("recommendation/recommender", exist_ok=True)
    joblib.dump(tfidf, "recommendation/recommender/tfidf_vectorizer.pkl")
    joblib.dump(model, "recommendation/recommender/job_recommendation_model.pkl")

    print("✅ TF-IDF vectorizer and Logistic Regression model trained and saved successfully.")

if __name__ == "__main__":
    train_model()




# # train_model.py
# import os
# from recommendation.utils import load_and_prepare_data, create_training_pairs, vectorize_text
# from sklearn.linear_model import LogisticRegression
# import joblib

# def train_model():
#     # Load and preprocess
#     resumes_df, jobs_df = load_and_prepare_data("data/resumes.csv", "data/posted_jobs.csv")
#     pairs_df = create_training_pairs(resumes_df, jobs_df)
#     tfidf, X, y = vectorize_text(pairs_df)

#     # Train logistic regression
#     model = LogisticRegression(max_iter=1000)
#     model.fit(X, y)

#     # Save model and vectorizer
#     os.makedirs("recommendation/recommender", exist_ok=True)
#     joblib.dump(tfidf, "recommendation/recommender/tfidf_vectorizer.pkl")
#     joblib.dump(model, "recommendation/recommender/job_recommendation_model.pkl")
#     print("✅ Model training complete and saved.")

# if __name__ == "__main__":
#     train_model()
