"""
app/streamlit_app.py
Owner: Shilpi (Team Lead / Application & Integration)

Purpose:
    The professional dashboard that ties together preprocessing, the
    trained models, and explainability into a single interactive app.

Run locally:
    streamlit run app/streamlit_app.py

Deploy:
    Streamlit Community Cloud — see docs/deployment.md
"""

import os
import sys

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# Make src/ importable regardless of where streamlit is launched from
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from predict import predict_student, CAREER_TRACK_LABELS  # noqa: E402

st.set_page_config(
    page_title="Hackathon Success & Career Readiness Prediction System",
    page_icon="🎯",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Minimal custom styling — a calm slate/indigo palette instead of Streamlit's
# default red, and tighter typography for a more "product" feel.
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .main { background-color: #F7F8FA; }
    h1, h2, h3 { color: #1F2937; }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        border: 1px solid #E5E7EB;
    }
    .factor-pill {
        display: inline-block;
        background: #EEF2FF;
        color: #4338CA;
        border-radius: 999px;
        padding: 0.25rem 0.75rem;
        margin: 0.2rem;
        font-size: 0.85rem;
    }
    .improve-pill {
        display: inline-block;
        background: #FEF3C7;
        color: #92400E;
        border-radius: 999px;
        padding: 0.25rem 0.75rem;
        margin: 0.2rem;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🎯 Hackathon Success & Career Readiness Prediction System")
st.markdown(
    "Estimate entry-level Data/ job readiness and get a recommended "
    "career track, based on a model trained on skills, projects, "
    "internships, interviews — **and** hackathon history."
)

with st.expander("ℹ️  About this project & important disclaimer", expanded=False):
    st.markdown("""
    This tool predicts an **estimated probability** of job readiness using
    a machine learning model trained on a labeled dataset (see
    `data/README_DATA.md` for full data-integrity notes — the training
    data is currently **synthetic**, built to demonstrate the methodology).

    **Hackathon participation is treated as evidence of exposure and
    problem-solving practice — not, by itself, proof of expertise.**
    The model itself decides how much weight hackathons deserve relative
    to fundamentals, projects, deployment, internships, and interview
    performance; nothing here is scripted to reach a predetermined
    conclusion.

    > **This is an estimate produced from the training data and model
    > assumptions — not a guarantee of employment.**
    """)

st.divider()

# ---------------------------------------------------------------------------
# Input form
# ---------------------------------------------------------------------------
st.header("1. Enter Your Profile")

with st.form("student_input_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Background")
        age = st.number_input("Age", 18, 35, 22)
        degree = st.selectbox("Degree", ["B.Tech", "B.Sc", "M.Tech", "MCA", "BCA"])
        cgpa = st.slider("CGPA", 0.0, 10.0, 7.5, 0.1)

        st.subheader("Core Skills (0-10)")
        python_score = st.slider("Python", 0.0, 10.0, 6.0, 0.5)
        sql_score = st.slider("SQL", 0.0, 10.0, 5.5, 0.5)
        statistics_score = st.slider("Statistics", 0.0, 10.0, 5.5, 0.5)
        Power_BI_score = st.slider("Power BI", 0.0, 10.0, 6.0, 0.5)
        

    with col2:
        st.subheader("Advanced Skills (0-10)")
        ml_score = st.slider("Machine Learning", 0.0, 10.0, 5.5, 0.5)
        dl_score = st.slider("Deep Learning", 0.0, 10.0, 4.5, 0.5)
        genai_score = st.slider("Generative AI", 0.0, 10.0, 5.0, 0.5)

        st.subheader("Projects & Competitions")
        ml_projects = st.number_input("ML projects", 0, 30, 3)
        end_to_end_projects = st.number_input("End-to-end projects", 0, 30, 1)
        deployed_projects = st.number_input("Deployed projects", 0, 30, 0)
        kaggle_competitions = st.number_input("Kaggle competitions", 0, 50, 1)
        best_competition_rank = st.number_input(
            "Best competition rank (0 = never competed)", 0, 5000, 0
        )

    with col3:
        st.subheader("Hackathons & Real-World Exposure")
        hackathons_attended = st.number_input("Hackathons attended", 0, 50, 3)
        hackathons_won = st.number_input("Hackathons won", 0, 50, 0)
        finalist_status = st.number_input("Times reached finals", 0, 50, 0)
        github_projects = st.number_input("GitHub projects", 0, 100, 4)
        internship_months = st.number_input("Internship months", 0, 60, 0)
        certifications = st.number_input("Certifications", 0, 50, 2)

        st.subheader("Interview Readiness (0-10)")
        ml_interview_score = st.slider("ML interview score", 0.0, 10.0, 5.5, 0.5)
        communication_score = st.slider("Communication score", 0.0, 10.0, 6.0, 0.5)
        dsa_score = st.slider("DSA score", 0.0, 10.0, 5.5, 0.5)
        resume_score = st.slider("Resume score", 0.0, 10.0, 6.0, 0.5)
        mock_interview_score = st.slider("Mock interview score", 0.0, 10.0, 5.5, 0.5)

    submitted = st.form_submit_button("🔮 Predict Job Readiness", use_container_width=True)


# ---------------------------------------------------------------------------
# Prediction & results
# ---------------------------------------------------------------------------
if submitted:
    student_input = {
        "age": age, "cgpa": cgpa, "degree": degree,
        "python_score": python_score, "sql_score": sql_score,
        "statistics_score": statistics_score," Power_BI_score": Power_BI_score,"ml_score": ml_score,
        "dl_score": dl_score, "genai_score": genai_score,
        "ml_projects": ml_projects, "end_to_end_projects": end_to_end_projects,
        "deployed_projects": deployed_projects,
        "kaggle_competitions": kaggle_competitions,
        "best_competition_rank": best_competition_rank if best_competition_rank > 0 else None,
        "hackathons_attended": hackathons_attended, "hackathons_won": hackathons_won,
        "finalist_status": finalist_status, "github_projects": github_projects,
        "internship_months": internship_months, "certifications": certifications,
        "ml_interview_score": ml_interview_score,
        "communication_score": communication_score, "dsa_score": dsa_score,
        "resume_score": resume_score, "mock_interview_score": mock_interview_score,
    }

    try:
        result = predict_student(student_input)
    except FileNotFoundError:
        st.error(
            "Model files not found. Run `python src/preprocessing.py` then "
            "`python src/train.py` from the project root before launching the app."
        )
        st.stop()

    st.divider()
    st.header("2. Your Results")

    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown("#### Job Readiness")
        prob_pct = result["job_ready_probability"] * 100
        label = "✅ Job-Ready (estimated)" if result["job_ready"] == 1 else "🔶 Not Yet Ready (estimated)"
        st.metric("Estimated Job Readiness", f"{prob_pct:.0f}%", label)

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prob_pct,
            number={"suffix": "%"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#4338CA"},
                "steps": [
                    {"range": [0, 40], "color": "#FEE2E2"},
                    {"range": [40, 70], "color": "#FEF3C7"},
                    {"range": [70, 100], "color": "#D1FAE5"},
                ],
            },
        ))
        fig.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("#### Recommended Career Track")
        st.subheader(f"🎓 {result['career_track_label']}")

        track_df = pd.DataFrame(
            list(result["career_track_probabilities"].items()),
            columns=["Track", "Probability"],
        ).sort_values("Probability", ascending=True)

        fig2 = px.bar(
            track_df, x="Probability", y="Track", orientation="h",
            color="Probability", color_continuous_scale="Viridis",
        )
        fig2.update_layout(
            height=280, margin=dict(l=20, r=20, t=20, b=20),
            coloraxis_showscale=False, xaxis_title=None, yaxis_title=None,
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Explainable AI: What's Driving This Prediction")
    st.caption(
        "These are the features the trained model relies on most overall "
        "(global feature importance), shown together with your own values. "
        "This is not a guarantee — it reflects patterns in the training data."
    )

    factor_col, improve_col = st.columns(2)
    with factor_col:
        st.markdown("**💪 Strongest factors the model weighs most:**")
        if result["top_positive_factors"]:
            pills = "".join(
                f'<span class="factor-pill">{feat.replace("_", " ").title()}: {val}</span>'
                for feat, val in result["top_positive_factors"]
            )
            st.markdown(pills, unsafe_allow_html=True)
        else:
            st.write("No importance data available.")

    with improve_col:
        st.markdown("**📈 Areas to improve (below 5/10 among top factors):**")
        if result["areas_to_improve"]:
            pills = "".join(
                f'<span class="improve-pill">{feat.replace("_", " ").title()}</span>'
                for feat in result["areas_to_improve"]
            )
            st.markdown(pills, unsafe_allow_html=True)
        else:
            st.write("No major gaps detected among the top-weighted factors 🎉")

    st.info(
        "**Disclaimer:** This estimate is based on training data and model "
        "assumptions. It is **not** a guarantee of employment. Hackathon "
        "participation is one signal among many — use it alongside strong "
        "fundamentals, real projects, deployment experience, internships, "
        "and interview preparation.",
        icon="ℹ️",
    )


# ---------------------------------------------------------------------------
# Model performance section (static, computed from models/model_metadata.json)
# ---------------------------------------------------------------------------
st.divider()
st.header("3. Model Performance")

metadata_path = os.path.join(os.path.dirname(__file__), "..", "models", "model_metadata.json")
if os.path.exists(metadata_path):
    import json
    with open(metadata_path) as f:
        metadata = json.load(f)

    perf_col1, perf_col2 = st.columns(2)
    with perf_col1:
        st.markdown("**Job Readiness Model (Random Forest, tuned)**")
        jm = metadata["job_ready_model"]["test_metrics"]
        st.write(f"- Accuracy: {jm['accuracy']:.2%}")
        st.write(f"- ROC-AUC: {jm['roc_auc']:.3f}")
        st.write(f"- F1-score: {jm['f1']:.3f}")

    with perf_col2:
        st.markdown(f"**Career Track Model ({metadata['career_track_model']['algorithm']})**")
        st.write(f"- Accuracy: {metadata['career_track_model']['test_accuracy']:.2%}")
        st.write(f"- Macro F1: {metadata['career_track_model']['test_macro_f1']:.3f}")

    st.caption(
        "Metrics computed on a held-out test set the model never saw during "
        "training or tuning. See notebooks/04_model_comparison.ipynb for the "
        "full comparison across all candidate models."
    )
else:
    st.warning("Run `python src/train.py` to generate model performance metadata.")

st.divider()
st.caption(
    "Hackathon Success & AI Career Readiness Prediction System · "
    "Built by Shilpi, Vedika, Dushyant & Priyanshu · B.Tech CSE Group Project"
)
