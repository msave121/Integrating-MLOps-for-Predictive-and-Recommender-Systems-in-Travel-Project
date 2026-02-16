# ✈️ Travel Analytics & Recommendation System (ML + MLOps Capstone)

## 📌 Business Context

In the realm of travel and tourism, the intersection of data analytics and machine learning offers powerful opportunities to transform how travel experiences are designed and delivered.

This capstone project leverages three interconnected datasets — **Users**, **Flights**, and **Hotels** — to build intelligent systems that predict travel costs, classify users, and recommend hotels.  

Beyond model development, the project emphasizes **real-world MLOps practices**, including containerization, orchestration, CI/CD pipelines, automated workflows, and model tracking.

The objective is twofold:

- Enhance predictive capabilities in travel-related decision making  
- Gain hands-on experience deploying production-grade machine learning systems

---

## 📂 Datasets Overview

### 👤 Users Dataset

| Column | Description |
|--------|-------------|
| code | Unique user identifier |
| company | Associated company |
| name | User name |
| gender | Gender |
| age | Age |

---

### ✈️ Flights Dataset

| Column | Description |
|--------|-------------|
| travelCode | Travel identifier |
| userCode | Linked user ID |
| from | Origin |
| to | Destination |
| flightType | Flight class/type |
| price | Ticket price |
| time | Flight duration |
| distance | Travel distance |
| agency | Airline agency |
| date | Flight date |

---

### 🏨 Hotels Dataset

| Column | Description |
|--------|-------------|
| travelCode | Travel identifier |
| userCode | Linked user ID |
| name | Hotel name |
| place | Location |
| days | Stay duration |
| price | Price per day |
| total | Total stay cost |
| date | Booking date |

---

## 🎯 Project Objectives

### 1️⃣ Flight Price Regression Model
- Build a regression model to predict flight prices using `flights.csv`
- Perform feature engineering, training, and validation

---

### 2️⃣ REST API (Flask)
- Serve the regression model via a Flask REST API
- Enable real-time flight price predictions

---

### 3️⃣ Docker Containerization
- Package the application and model using Docker
- Ensure reproducible deployments across environments

---

### 4️⃣ Kubernetes Deployment
- Deploy containers using Kubernetes
- Enable scalability and load management

---

### 5️⃣ Workflow Automation with Apache Airflow
- Design DAGs for automated data processing and model workflows
- Orchestrate regression pipelines efficiently

---

### 6️⃣ CI/CD with Jenkins
- Implement Jenkins pipelines for:
  - Automated testing
  - Docker builds
  - Model deployment

---

### 7️⃣ Model Tracking with MLflow
- Track experiments and model versions
- Manage lifecycle of regression models

---

### 8️⃣ Gender Classification Model
- Build and deploy a classification model to predict user gender

---

### 9️⃣ Travel Recommendation System + Streamlit App
- Develop a hotel recommendation engine based on user behavior
- Create a Streamlit web application for:
  - Recommendations
  - Visual insights
  - Interactive exploration

---

## 🛠 Tech Stack

- **Python**
- **Scikit-learn**
- **Flask**
- **Docker**
- **Kubernetes**
- **Apache Airflow**
- **Jenkins**
- **MLflow**
- **Streamlit**
- **Pandas / NumPy**
- **Git & GitHub**

---

## 🚀 Key Learning Outcomes

- End-to-end ML pipeline development
- Production deployment using Docker & Kubernetes
- CI/CD implementation with Jenkins
- Workflow orchestration via Airflow
- Experiment tracking with MLflow
- Building interactive ML applications using Streamlit

---

## 📈 Future Enhancements

- Real-time streaming recommendations  
- Advanced deep learning models  
- Cloud deployment (AWS/GCP/Azure)  
- Monitoring with Prometheus & Grafana  

---

## 👩‍💻 Author

**Manasvi Save**

---

⭐ If you find this project useful, feel free to star the repository!
