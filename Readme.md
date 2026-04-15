# 🛡️ MedGuard AI

### Real-Time Health Insurance Claim Fraud Detection Platform

---

## 🚀 Overview

**MedGuard AI** is an intelligent, real-time fraud detection platform designed to identify suspicious health insurance claims using a combination of **machine learning, rule-based systems, and medical logic validation**.

The platform enables:

* 👤 Users to submit insurance claims
* 🤖 AI to analyze claims instantly
* 🧑‍💼 Admins to review, approve, or reject claims
* 📊 A dashboard to monitor fraud patterns and trends

It simulates a **production-grade AI-powered insurance system** with explainability, real-time insights, and structured workflows.

---

## ❗ Problem Statement

Health insurance fraud is a major issue worldwide, causing billions in losses annually. Fraudulent claims often involve:

* Inflated billing amounts
* Unnecessary or fake procedures
* Mismatched diagnosis and treatments
* Repeated or suspicious claim patterns

Traditional systems rely heavily on manual review, which is:

* ❌ Slow
* ❌ Error-prone
* ❌ Not scalable

---

## 🎯 Objectives

This project aims to:

1. ✅ Develop an AI model to detect fraudulent claims
2. ✅ Build a real-time claim submission and analysis system
3. ✅ Implement a hybrid fraud detection engine
4. ✅ Provide explainable AI outputs
5. ✅ Create role-based dashboards for users and admins
6. ✅ Evaluate model performance using metrics like:

   * Accuracy
   * Precision
   * Recall
   * F1-score

---

## 🧠 Core Features

### 👤 User Features

* Register & login
* Submit insurance claims
* View claim status
* View AI-generated summaries
* Track claim timeline

### 🧑‍💼 Admin Features

* View all claims
* AI fraud analysis panel
* Approve / Reject claims
* View anomaly alerts
* Provider leaderboard
* Real-time dashboard

### 🤖 AI Features

* Fraud probability scoring
* Risk level classification (Low / Medium / High)
* Diagnosis–Procedure consistency check
* Rule-based anomaly detection
* Human-readable explanations

---

## 🧪 Machine Learning Approach

### 📊 Dataset Used

* Healthcare Provider Fraud Detection Dataset (Kaggle)

### 🔍 Algorithms Tested

We evaluated multiple machine learning models:

* Logistic Regression
* Decision Tree
* Random Forest
* Gradient Boosting
* AdaBoost
* K-Nearest Neighbors
* **XGBoost (Final Selected Model)**

---

## 🏆 Best Model: XGBoost

### Why XGBoost?

* Works extremely well on structured/tabular data
* Handles non-linear relationships
* Robust against overfitting
* High performance in fraud detection tasks

---

## 📈 Model Performance

| Metric    | Score (Approx) |
| --------- | -------------- |
| Accuracy  | ~91.04%        |
| Precision | ~51.52%        |
| Recall    | ~67.33%        |
| F1 Score  | ~58.37%        |

👉 **XGBoost outperformed all other models**, making it the final choice for deployment.

---

## ⚙️ Hybrid Fraud Engine (Advanced Logic)

The final fraud decision is NOT based only on ML.

Instead, we use a **Hybrid Scoring System**:

```
Final Fraud Score =
    0.35 * ML Model Probability +
    0.40 * Rule-Based Score +
    0.25 * Medical Consistency Score
```

### 🔎 Components

#### 1. ML Model

* Predicts fraud probability from patterns in data

#### 2. Rule-Based Engine

Checks:

* High claim amount
* High procedure count
* Emergency misuse
* Out-of-pocket anomalies

#### 3. Medical Consistency Engine

* Validates diagnosis vs procedure
* Flags mismatches (e.g., fever + major surgery)

---

## 🏥 Medical Intelligence Layer

We implemented:

### 📘 Diagnosis Code Dictionary

Example:

* `D100 → Routine Consultation`
* `D200 → Cardiac Emergency`

### 🧾 Procedure Code Dictionary

Example:

* `P200 → Blood Test`
* `P460 → Major Surgery`

### 🔍 Consistency Check

Detects:

* Unusual combinations
* Illogical medical patterns

---

## 🖥️ Dashboard & UI

Built using **Streamlit**, the app includes:

### 🎨 Features

* Clean, modern UI
* Role-based access
* Real-time updates
* Interactive charts
* AI explanation panels

---

## 🧱 Tech Stack

### 🔹 Backend & ML

* Python
* Scikit-learn
* XGBoost
* Pandas / NumPy
* Imbalanced-learn (SMOTE)

### 🔹 Frontend

* Streamlit

### 🔹 Database

* SQLite (local development)

### 🔹 Tools

* Joblib (model saving)
* KaggleHub (dataset)

---

## 📂 Project Structure

```
medguard_ai/
│
├── app.py
├── pages/
│   ├── User Dashboard
│   ├── Submit Claim
│   ├── My Claims
│   ├── Admin Dashboard
│   ├── All Claims
│   └── Claim Review
│
├── services/
│   ├── predictor.py
│   ├── mapper.py
│   ├── database.py
│   ├── auth.py
│   ├── explanations.py
│   ├── medical_rules.py
│   └── codebook.py
│
├── models/
├── artifacts/
├── data/
└── notebooks/
```

---

## 🛠️ Getting Started

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/medguard-ai.git
cd medguard-ai
```

---

### 2️⃣ Create virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
```

---

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Run the app

```bash
streamlit run app.py
```

---

## 🔐 Default Credentials

### Admin

```
Email: admin@medguard.ai
Password: admin123
```

### User

```
Email: aman@example.com
Password: user123
```

---

## 🧪 How to Use

### 👤 As a User

1. Register / Login
2. Go to **Submit Claim**
3. Fill claim details
4. View AI prediction
5. Track claim in **My Claims**

---

### 🧑‍💼 As an Admin

1. Login as admin
2. Open **Admin Dashboard**
3. View claims
4. Analyze AI insights
5. Approve / Reject claims

---

## 🧠 Example Fraud Case

Try this:

* Diagnosis: Routine Consultation
* Procedure: Major Surgery
* Claim Amount: ₹95,000
* Procedure Count: 5
* Emergency admission

👉 Expected: **High Risk**


---

## ⭐ If you like this project

Give it a ⭐ on GitHub and share your feedback!

