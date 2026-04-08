# BankAI - Premium Smart Banking Assistant

BankAI is a sophisticated, multi-agent banking assistant designed to provide a premium, corporate-grade banking experience. Built with **LangGraph** for powerful multi-agent orchestration and **Streamlit** for a high-end visual interface, it handles everything from general queries to secure funds transfers and location-based searches.

## Features

### Premium UI/UX
- **Corporate Aesthetic**: A sleek Navy Blue (#0A1628) and Gold (#C9A84C) theme.
- **Modern Typography**: High-end font pairing using *Playfair Display* for headings and *Inter* for body text.
- **Responsive Design**: Custom-built HTML/CSS components for a seamless, premium feel across all pages.
- **Dark/Light Mode**: Full support for both themes with an easy-to-use toggle.

### Multi-Agent Intelligence
- **Main Assistant**: Routes user intent and handles general banking knowledge.
- **Account Agent**: Provides detailed information on products, loans, and interest rates.
- **Funds Transfer Agent**: Guides users through NEFT, RTGS, IMPS, and UPI transfers.
- **Location Agent**: Delivers high-precision Google Maps links for branches and ATMs based on specific user locations.

### Advanced Capabilities
- **Multi-Language Support**: Chat naturally in English, Hindi, Kannada, Malayalam, Tamil, or Telugu.
- **Zero-Login Guest Mode**: Access general banking features and branch location services instantly without an account.
- **Secure Architecture**: Integrated with a persistent SQLite memory systems and a robust MySQL backend for user management.

## Tech Stack
- **Frontend**: Streamlit (Python)
- **Agent Orchestration**: LangGraph
- **LLM**: Google Gemini 2.5 Flash (via Google Generative AI)
- **Database**: 
  - MySQL (User Auth, Accounts, Transactions)
  - SQLite (Agent persistent memory)

## Setup & Installation

### 1. Database Setup
Execute the provided `setup_db.sql` script in your MySQL environment to initialize the schema:
```sql
SOURCE setup_db.sql;
```

### 2. Environment Configuration
Create a `.env` file in the root directory and add your credentials:
```env
GOOGLE_API_KEY=your_gemini_api_key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=bank_chatbot
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
streamlit run streamlit_app.py
```

## Screen Previews
*Landing Page • Login/Signup • Bank Selection • Chat Interface*

---
*Built with Modern Banking Standards*
