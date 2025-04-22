---
title: Email Classification Support System
emoji: 📧
colorFrom: blue
colorTo: indigo
sdk: docker
sdk_version: "20.10.17"
app_file: app.py
pinned: false
---

# Email Classification Support System

This repository provides an end-to-end system for classifying customer support emails into predefined categories (Incident, Request, Problem, Change). The system automatically masks sensitive personal and support information, translates content to English, and uses a machine learning pipeline to classify the email.

---

## 📁 Project Structure

```
.
├── app.py                  # Main Flask application
├── api.py                  # calling test file
├── models.py               # Model training and prediction class
├── utils.py                # PII masking and translation logic
├── Research/
│   └── final_marked_dataset.zip  
│   └── base_code.ipynb
├── final_pipeline.pkl      # Saved ML pipeline
├── requirements.txt        # Project dependencies
├── Dockerfile              # To build and deploy application
├── Documentation Report
├── Postman Collection/
│   └── Email Classification Support System.postman_collection
└── README.md               
```

---

## 🚀 Features

- **PII Detection and Masking**
- **Multilingual Translation** to English
- **Model Selection and Training**
- **Email Type Classification** into:
  - Incident
  - Problem
  - Request
  - Change
- **FLASK API** endpoint for live predictions **(Easy to Use, No Cost Deployment)**

---

## 🧪 Requirements

Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Unzip the dataset for training present under Research\final_masked_dataset.zip

## 🧪 Testing

Run the provided URL on Postman on IDE:

```bash
https://AkshatJain20092002-Email-Classification-Support-System.hf.space/classify
```

Take **POST** request:

```bash
{
    "email_body": "Input email"
}
```

**Output Format**

```bash

{
    "input_email_body": "string containing the email", 
    "list_of_masked_entities": [ 
    { 
        "position": [start_index, end_index], 
        "classification": "entity_type", 
        "entity": "original_entity_value" 
    } 
    ], 
    "masked_email": "string containing the masked email", 
    "category_of_the_email": "string containing the class" 
} 

```


## 🛡️ Data Privacy

All personally identifiable information (PII) and sensitive card information (PCI) are masked before processing using custom regex and multilingual NER **leveraging no-cost enabled models.** This masking is achieved using completely free available resources.

---

## 📬 Contact

Maintained by: Akshat Jain

---

## 📄 License

This project is licensed under the MIT License.

