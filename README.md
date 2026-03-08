# Smart Lost-and-Found Platform

## Overview

The Smart Lost-and-Found Platform is an AI-assisted system designed to improve the process of reporting, matching, and recovering lost items. Traditional lost-and-found systems usually function as simple registers where items are manually recorded. These systems depend heavily on accurate human memory and exact descriptions, which often leads to mismatches between lost and found reports.

This platform enhances the process by introducing intelligent mechanisms that help reconstruct item descriptions, semantically match lost and found reports, estimate recovery probability, and ensure secure item claims. The system actively assists users in reconnecting lost items with their rightful owners rather than simply storing records.

---

## Key Features

### Memory-Based Item Description

When reporting a lost item, the system assists users in recalling additional details through intelligent follow-up questions. This process helps reconstruct missing information and generates a richer description of the item, improving the accuracy of future matches.

### Semantic Matching

The platform compares lost item descriptions with newly reported found items using semantic similarity instead of simple keyword matching. This allows the system to identify matches even when different wording is used to describe the same object.

### Image-Based Item Reporting

Users who find items can upload images along with captions. The system analyzes both textual descriptions and images to determine potential matches with existing lost item reports.

### Automatic Match Notification

When a strong similarity is detected between a lost item report and a found item submission, the system automatically notifies the potential owner through email.

### Recovery Probability Prediction

The system estimates the likelihood of successfully recovering a lost item. The probability score is dynamically calculated based on multiple factors such as description similarity, time elapsed since the loss, and the number of potential matches.

### Visual Item Reconstruction

The platform can generate a visual preview of a lost item based on the user's description. This helps users verify whether a found item closely resembles the item they reported missing.

### Fraud Detection

To prevent false claims, the system evaluates the legitimacy of item claims using verification questions and behavioral analysis. Suspicious claims can be flagged for further review.

### QR-Based Secure Pickup

Once a claim is verified, a unique QR code is generated for item collection. The QR code is scanned during pickup to validate the claim and prevent duplicate retrievals.

---

## System Workflow

1. **Lost Item Reporting**

   * User reports a lost item.
   * The system asks follow-up questions to enrich the description.
   * A detailed item profile is generated and stored.

2. **Found Item Reporting**

   * A finder uploads an image and description of the item.
   * The system analyzes the report and compares it with existing lost items.

3. **Matching Process**

   * The platform calculates semantic similarity between lost and found items.
   * Potential matches are identified.

4. **Notification**

   * If a strong match is detected, the potential owner receives an email notification.

5. **Claim Verification**

   * The user answers verification questions to confirm ownership.
   * Fraud detection checks are applied.

6. **Secure Pickup**

   * A QR code is generated for pickup.
   * The item is verified and logged during collection.

---


## AI Models and Libraries

The platform integrates multiple machine learning models and supporting libraries to enable intelligent matching, prediction, and verification.

### Stable Diffusion XL – Text-to-Image

Used to generate visual representations of lost items based on textual descriptions. This helps users verify whether a found item resembles the object they reported missing.

### BLIP – Image Captioning

Automatically generates textual descriptions for uploaded images of found items. These captions help improve the matching process by converting visual information into searchable text.

### MiniLM – Text Embeddings

Converts lost item descriptions and captions into semantic vector embeddings. These embeddings capture the meaning of the text rather than relying on exact keywords.

### CLIP – Image Embeddings

Processes uploaded images and converts them into vector representations that capture visual features. These embeddings allow images to be compared with textual descriptions and other images.

### ChromaDB – Vector Search

Stores and indexes embeddings generated from text and images. It performs similarity search to efficiently identify potential matches between lost and found items.

### Gemini – Question Generation and Fraud Detection

Generates intelligent follow-up questions to help users recall missing details when reporting lost items. It also assists in fraud detection by generating verification questions and evaluating claim responses.

### XGBoost – Recovery Probability Prediction

Predicts the likelihood that a lost item will be successfully recovered. The model analyzes factors such as similarity scores, time since the item was reported lost, and the number of potential matches.

### QRCode Library – QR Code Generation

Generates unique QR codes for verified item claims. These QR codes are scanned during pickup to securely validate ownership and prevent duplicate claims.

---

## Installation

### 1. Clone the Repository

```
git clone https://github.com/your-username/LostNFound.git
cd LostNFound
```

### 2. Install Backend Dependencies

```
cd backend
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```
cd frontend
npm install
```

### 4. Start the Backend Server

```
python main.py
```

### 5. Start the Frontend

```
npm start
```

---

## Usage

1. Report a lost item by providing an initial description.
2. Answer follow-up questions to improve the item profile.
3. Upload found items with images and captions.
4. The system automatically identifies potential matches.
5. Users receive notifications if a possible match is found.
6. Verified owners can claim their items using secure QR-based pickup.

---

