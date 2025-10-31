# Bank Document Validator

This project is a full-stack application that validates bank documents (cheques or statements) by comparing extracted information from uploaded images or PDFs with manually entered values. It uses OpenAI's GPT-4o vision model to analyze document content and return structured validation results.

## Features

- Upload bank cheques or statements (PDF, JPG, PNG)
- Extract and validate:
  - Account Holder Name
  - Account Number
  - IFSC Code
- Compare extracted values with user input
- Highlight matches, mismatches, and near matches
- Streamlit frontend with styled result table
- Flask backend with GPT-4o integration

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Flask
- **AI Model**: OpenAI GPT-4o (vision + text)
- **Image Processing**: pdf2image, Pillow
- **Validation Logic**: fuzzywuzzy for near-match detection


