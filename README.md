# 📚 Installation & User Guide
## 1. Clone the repository
```bash
git clone https://github.com/seansukamto/adapt-learn.git
cd adapt-learn
```

## 2. Install required packages
```bash
pip install -r requirements.txt
```
## 3. (Optional) Add OpenAI API Key
If you want to enable AI-generated quiz questions, you can add your OpenAI API key:
```bash
cd .streamlit
```
Create a file called `secrets.toml` with the following content:
```toml
OPENAI_API_KEY = "your-api-key"
```

## 4. Run the app
From the root directory:
```bash
streamlit run streamlit_app.py
```
