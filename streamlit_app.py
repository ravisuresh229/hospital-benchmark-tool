import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from pptx import Presentation
from pptx.util import Inches
import tempfile
import os
from datetime import datetime

HCAHPS_PATH = 'HCAHPS.csv'
HOSPITAL_INFO_PATH = 'Hospital_General_Information.csv'

@st.cache_data
def load_hospital_info():
    return pd.read_csv("https://www.dropbox.com/scl/fi/fq5o8a6evwpsfzutjp7uw/Hospital_General_Information.csv?rlkey=c60s0se15d6nzs40mm19a2q5v&st=li48t6ft&dl=1", dtype=str)

@st.cache_data
def load_hcahps_data():
    df = pd.read_csv("https://www.dropbox.com/scl/fi/d35e3po3qfyaw7fz3qend/HCAHPS.csv?rlkey=pw76uj8z5270ks7izz6esx62r&st=ugsr5p6s&dl=1", dtype=str)
    df.columns = df.columns.str.strip()
    df['HCAHPS Answer Percent'] = pd.to_numeric(df['HCAHPS Answer Percent'], errors='coerce')
    return df

st.title('🏥 Hospital HCAHPS Benchmarking Tool')

with st.expander('ℹ️ What do these metrics mean? (Click to expand)', expanded=False):
    st.markdown('''
**How to interpret the table and chart:**
- **Hospital**: The selected hospital's average score for each metric (higher is better).
- **State Avg**: The average score for all hospitals in the same state.
- **National Avg**: The average score for all hospitals in the U.S.
- **vs State / vs National**: How much higher or lower the hospital is compared to the state/national average (green = better, red = worse).

**Metric definitions:**
- **Nurse Communication**: % of patients who said nurses "always" communicated well.
- **Doctor Communication**: % of patients who said doctors "always" communicated well.
- **Staff Responsiveness**: % of patients who said they "always" received help as soon as they wanted.
- **Care Transition**: % of patients who "strongly agree" they understood their care when leaving the hospital.
- **Discharge Info**: % of patients who said staff "did" give them discharge information.
- **Care Cleanliness**: % of patients who said their room was "always" clean.
- **Quietness**: % of patients who said the area around their room was "always" quiet at night.
- **Recommend**: % of patients who would "definitely recommend" the hospital.

**How to use this:**
- Look for green cells: These are areas where the hospital outperforms the benchmark.
- Look for red cells: These are areas where the hospital underperforms and may need improvement.
- Use the chart to quickly spot strengths and weaknesses compared to state and national averages.
''')

df_info = load_hospital_info()
df_hcahps = load_hcahps_data()
# st.write("All unique HCAHPS Answer Descriptions:", df_hcahps['HCAHPS Answer Description'].unique())
hospital_names = df_info['Facility Name'].sort_values().unique()
hospital = st.selectbox('Select Hospital', hospital_names)

hospital_row = df_info[df_info['Facility Name'] == hospital].iloc[0]
hospital_id = hospital_row['Facility ID']
hospital_state = hospital_row['State']

# Define the measures and the answer description to use for each
all_measures = [
    ("Nurse Communication", "H_COMP_1_A_P"),
    ("Doctor Communication", "H_COMP_2_A_P"),
    ("Staff Responsiveness", "H_COMP_3_A_P"),
    ("Care Transition", "H_COMP_5_A_P"),
    ("Discharge Info", "H_COMP_6_Y_P"),
    ("Care Cleanliness", "H_CLEAN_HSP_A_P"),
    ("Quietness", "H_QUIET_HSP_A_P"),
    ("Recommend", "H_RECMND_DY"),
]

metric_options = [m[0] for m in all_measures]
selected_metrics = st.multiselect(
    "Select metrics to display", metric_options, default=metric_options
)
measures = [m for m in all_measures if m[0] in selected_metrics]

def match_answer(series, answer):
    return series.str.strip().str.lower() == answer.strip().lower()

comparison = []
for label, measure_id in measures:
    hosp_score = df_hcahps[
        (df_hcahps['Facility ID'] == hospital_id) &
        (df_hcahps['HCAHPS Measure ID'] == measure_id)
    ]['HCAHPS Answer Percent'].mean()
    state_avg = df_hcahps[
        (df_hcahps['State'] == hospital_state) &
        (df_hcahps['HCAHPS Measure ID'] == measure_id)
    ]['HCAHPS Answer Percent'].mean()
    nat_avg = df_hcahps[
        (df_hcahps['HCAHPS Measure ID'] == measure_id)
    ]['HCAHPS Answer Percent'].mean()
    comparison.append({
        'Measure': label,
        'Hospital': hosp_score,
        'State Avg': state_avg,
        'National Avg': nat_avg,
        'vs State': hosp_score - state_avg if pd.notnull(hosp_score) and pd.notnull(state_avg) else None,
        'vs National': hosp_score - nat_avg if pd.notnull(hosp_score) and pd.notnull(nat_avg) else None
    })

comp_df = pd.DataFrame(comparison)

# --- Display Table ---
st.subheader('Comparison Table')
st.dataframe(comp_df[['Measure', 'Hospital', 'State Avg', 'National Avg', 'vs State', 'vs National']].style.applymap(
    lambda v: 'background-color: #d4edda' if isinstance(v, (int, float)) and v > 0 else ('background-color: #f8d7da' if isinstance(v, (int, float)) and v < 0 else ''),
    subset=['vs State', 'vs National']
))

# --- Visualization ---
st.subheader('Benchmark Chart')
fig = go.Figure()
fig.add_trace(go.Bar(x=comp_df['Measure'], y=comp_df['Hospital'], name='Hospital'))
fig.add_trace(go.Bar(x=comp_df['Measure'], y=comp_df['State Avg'], name='State Avg'))
fig.add_trace(go.Bar(x=comp_df['Measure'], y=comp_df['National Avg'], name='National Avg'))
fig.update_layout(barmode='group', yaxis_title='Score (%)', xaxis_title='Measure')
st.plotly_chart(fig, use_container_width=True)

# --- PowerPoint Export ---
def create_pptx(comp_df, hospital, chart_path):
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    title = slide.shapes.title
    title.text = f"HCAHPS Benchmark Report: {hospital}"
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(1.2), Inches(9), Inches(0.5))
    tf = txBox.text_frame
    tf.text = f"Analysis Date: {datetime.now().strftime('%Y-%m-%d')}"
    # Add table
    rows, cols = comp_df.shape
    table = slide.shapes.add_table(rows+1, cols, Inches(0.5), Inches(1.8), Inches(9), Inches(0.8+rows*0.3)).table
    for j, col in enumerate(comp_df.columns):
        table.cell(0, j).text = col
    for i in range(rows):
        for j in range(cols):
            val = comp_df.iloc[i, j]
            if pd.notnull(val):
                if isinstance(val, (int, float, float)):
                    table.cell(i+1, j).text = str(round(val, 2))
                else:
                    table.cell(i+1, j).text = str(val)
            else:
                table.cell(i+1, j).text = ""
    # Add chart image
    slide.shapes.add_picture(chart_path, Inches(0.5), Inches(2.2+rows*0.3), Inches(7))
    return prs

def save_chart_as_image(fig):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    fig.write_image(tmp.name)
    return tmp.name

if st.button('Download PowerPoint Report'):
    chart_img = save_chart_as_image(fig)
    pptx = create_pptx(comp_df, hospital, chart_img)
    tmp_pptx = tempfile.NamedTemporaryFile(delete=False, suffix='.pptx')
    pptx.save(tmp_pptx.name)
    with open(tmp_pptx.name, 'rb') as f:
        st.download_button('Download Report', f, file_name=f"{hospital}_HCAHPS_Benchmark_{datetime.now().strftime('%Y%m%d')}.pptx")
    os.remove(chart_img)
    os.remove(tmp_pptx.name)

st.info('If you see errors, please check the column names in your CSVs and adjust them in the code as needed.')