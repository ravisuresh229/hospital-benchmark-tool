# 🏥 Hospital HCAHPS Benchmarking Tool

A Streamlit web app for benchmarking hospital HCAHPS (Hospital Consumer Assessment of Healthcare Providers and Systems) survey results. Compare your hospital’s performance to state and national averages, visualize strengths and weaknesses, and export professional PowerPoint reports for presentations.

---

## 📸 Example Screenshots

### App Interface
![App Screenshot](example_screenshot_app.png)

### PowerPoint Export
![PowerPoint Export](example_screenshot_pptx.png)

---

## 🚀 Running Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/hcahps-benchmark-tool.git
   cd hcahps-benchmark-tool
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app:**
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Open your browser:**
   - Go to [http://localhost:8501](http://localhost:8501)

---

## ☁️ Deploy on Streamlit Cloud

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/yourusername/hcahps-benchmark-tool/main/streamlit_app.py)

---

## 📋 Features
- Select any hospital and compare HCAHPS metrics to state and national averages
- Interactive bar chart with clear color coding and value labels
- Download a polished PowerPoint report with table and chart, ready for presentations
- Easy-to-use, modern UI

---

## 📝 Notes
- Example screenshots (`example_screenshot_app.png`, `example_screenshot_pptx.png`) should be added to the repo for full README rendering.
- Data is loaded from public Dropbox links; you can update these in `streamlit_app.py` if needed.
