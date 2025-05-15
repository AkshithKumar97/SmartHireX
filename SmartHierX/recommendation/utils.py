# recommendation/utils.py
import os
import pandas as pd
import numpy as np
import re
import string
import PyPDF2
import docx2txt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STOPWORDS = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()


#Cleaning the text
#Removing digits, punctuation, and stopwords, and lemmatizing the words

def extract_text_from_file(file_path):
    if file_path.endswith('.pdf'):
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
            return text
    elif file_path.endswith('.docx'):
        return docx2txt.process(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()



def clean_text(text):
    if pd.isnull(text):
        return ""
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = text.split()
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in STOPWORDS]
    return " ".join(tokens)

def combine_resume_fields(row):
    fields = [row.get('skills', ''), row.get('degree_names', ''),
              row.get('positions', ''), row.get('responsibilities', ''),row.get("experience", "")]
    return clean_text(" ".join(map(str, fields)))

def combine_job_fields(row):
    fields = [row.get('Skills Required', ''), row.get('Qualifications', ''),
              row.get('Role', ''), row.get('Roles and Responsibilities', ''),row.get("job_description", "")]
    return clean_text(" ".join(map(str, fields)))

def load_and_prepare_data(resume_csv, jobs_csv):
    resumes_df = pd.read_csv(os.path.join(BASE_DIR, "data/resumes.csv"))
    jobs_df = pd.read_csv(os.path.join(BASE_DIR, "data/posted_jobs.csv"))


    # Combine and clean text fields
    resumes_df['combined_text'] = resumes_df.apply(combine_resume_fields, axis=1)
    jobs_df['combined_text'] = jobs_df.apply(combine_job_fields, axis=1)

    return resumes_df, jobs_df

def create_training_pairs(resumes_df, jobs_df, positive_ratio=0.2):
    """
    Create resume-job pairs labeled as 1 (match) and 0 (non-match).
    For each resume, create one positive and multiple negative pairs.
    """
    pairs = []

    for _, resume in resumes_df.iterrows():
        # Sample 1 positive job (mock relevant)
        matched_job = jobs_df.sample(1).iloc[0]
        pairs.append((resume['combined_text'], matched_job['combined_text'], 1))

        # Sample negative jobs (not matched)
        negative_sample_count = int((1 / positive_ratio) - 1)
        negative_jobs = jobs_df.sample(negative_sample_count)
        for _, neg_job in negative_jobs.iterrows():
            pairs.append((resume['combined_text'], neg_job['combined_text'], 0))

    df_pairs = pd.DataFrame(pairs, columns=['resume_text', 'job_text', 'label'])
    return df_pairs

    # Create resume-job pairs with labels: 1 if matched, 0 if not
    # pairs = []
    # for _, resume in resumes_df.iterrows():
    #     matched_job = jobs_df.sample(1).iloc[0]  # Assume this job is relevant (mock)
    #     pairs.append((resume['combined_text'], matched_job['combined_text'], 1))

    #     # Add negative examples
    #     negative_jobs = jobs_df.sample(int(1/positive_ratio - 1))
    #     for _, neg_job in negative_jobs.iterrows():
    #         pairs.append((resume['combined_text'], neg_job['combined_text'], 0))

    # df_pairs = pd.DataFrame(pairs, columns=['resume_text', 'job_text', 'label'])
    # return df_pairs

def vectorize_text(df_pairs):
    corpus = df_pairs['resume_text'] + " " + df_pairs['job_text']
    tfidf = TfidfVectorizer(max_features=5000)
    X = tfidf.fit_transform(corpus)
    return tfidf, X, df_pairs['label']
