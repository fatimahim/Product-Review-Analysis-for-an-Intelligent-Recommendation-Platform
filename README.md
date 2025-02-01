# Product Review Analysis for an Intelligent Recommendation Platform

This project focuses on analyzing product reviews by fine-tuning a large language model (LLM) **T5** on **43,000** reviews with their sentiments. The goal is to build an intelligent recommendation platform using **Django** that provides **ratings, insights, and sentiment analysis** for products based on user reviews.

## 🚀 Features

### 📊 Sentiment Analysis Model
- **Model**: Fine-tuned T5 on **43K** reviews with sentiment labels.
- **Purpose**: Predicts sentiment (Positive, Neutral, Negative) of product reviews.

### 🏆 Large-Scale Product Review Analysis
- **Data**: Applied model on **3 million** Amazon product reviews.
- **Storage**: All processed data is stored in **MongoDB**.
- **Insights**:
  - ✅ **Product Ratings** (Average Score)
  - 📝 **Review Sentiments** (Positive, Neutral, Negative)
  - 📊 **Trends and Insights**

## 🛠 Technology Stack

- **Component** | **Technology**
  - Backend: Django Framework
  - Frontend: Django Templates, HTML, CSS
  - Sentiment Analysis Model: Fine-tuned T5 (LLM)
  - Database: MongoDB

## 📋 Implementation Details

### Data Preparation
- **Fine-Tuned LLM**: Trained on **43K** labeled product reviews.
- **Data Processing**:
  - Collected and preprocessed **3 million** Amazon reviews.
  - Applied fine-tuned model to classify sentiment.

### Platform Development
- Built using **Django** to ensure scalability and user-friendly interaction.
- Displays **product-wise average ratings** and **sentiment insights**.

## 🎯 User Interaction

Users can:
- 🛂 **Log in or out**.
- 📢 **View product ratings and reviews**.
- 🔍 **Explore sentiment insights** for better purchasing decisions.

## 🖥️ How to Run

1. **Clone the repository**:
   ```bash
   git clone https://github.com/fatimahim/Product-Review-Analysis-for-an-Intelligent-Recommendation-Platform
   cd product-review-analysis
   ```


3. **Set Up MongoDB**:
   ```bash
   sudo service mongod start
   ```

4. **Run Django Migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Start the Server**:
   ```bash
   python manage.py runserver
   ```

   Now, access the platform at **http://127.0.0.1:8000**.

## 📌 Future Enhancements
- 🔍 **Advanced Recommendation System**
- 📈 **Data Visualization Dashboards**
- 🌍 **Multi-Language Sentiment Analysis**


## 🤝 Contributing
Feel free to fork this repository and submit pull requests.

## 📧 Contact
For any inquiries, reach out via [fatima2000him@gmail.com].

