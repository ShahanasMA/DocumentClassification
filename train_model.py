import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

DATASET_PATH = "dataset"

texts = []
labels = []

# -------- LOAD DATASET --------
for category in os.listdir(DATASET_PATH):
    cat_path = os.path.join(DATASET_PATH, category)

    if os.path.isdir(cat_path):
        for file in os.listdir(cat_path):

            if file.endswith(".txt"):
                with open(os.path.join(cat_path, file), "r", encoding="utf-8", errors="ignore") as f:
                    texts.append(f.read())
                    labels.append(category)

print("Loaded", len(texts), "documents")

# -------- SPLIT DATA --------
X_train, X_test, y_train, y_test = train_test_split(
    texts,
    labels,
    test_size=0.25,
    random_state=42
)

# -------- MODEL --------
model = Pipeline([
    ("tfidf", TfidfVectorizer(
        stop_words="english",
        max_features=5000,
        ngram_range=(1,2)
    )),
    ("clf", SVC(
        kernel="linear",
        probability=True
    ))
])

# -------- TRAIN --------
model.fit(X_train, y_train)

# -------- TEST --------
pred = model.predict(X_test)

accuracy = accuracy_score(y_test, pred)

print("Model Accuracy:", accuracy)

# -------- SAVE MODEL --------
joblib.dump(model, "document_classifier.pkl")

print("Model saved")
