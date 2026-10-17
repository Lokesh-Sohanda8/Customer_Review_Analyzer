"""Streamlit dashboard for analyzing customer feedback through a FastAPI backend."""

from collections import Counter
import os

import requests
import streamlit as st

from database import init_db, save_results, load_history, DB_FILE


def get_backend_base_url() -> str:
    """Read the API base URL from Streamlit secrets or environment variables.

    Locally, the default points to a FastAPI server running on port 8000.
    In Streamlit Community Cloud, set BACKEND_API_URL in the app's Secrets.
    """
    value = None
    try:
        value = st.secrets.get("BACKEND_API_URL")
    except Exception:
        # No local secrets.toml is required when using the default URL.
        pass

    value = value or os.getenv("BACKEND_API_URL") or "http://127.0.0.1:8000"
    return value.strip().rstrip("/")


API_URL = f"{get_backend_base_url()}/analyze_review"
REQUEST_TIMEOUT_SECONDS = 90

init_db()

st.title("📝 Customer Feedback Analyzer")
st.write("Paste your customer reviews below, one review per line.")
st.caption(f"Analysis API: {get_backend_base_url()}")

reviews_text = st.text_area("Reviews", height=200)

if st.button("Analyze"):
    reviews = [line.strip() for line in reviews_text.splitlines() if line.strip()]

    if not reviews:
        st.warning("Please paste at least one review.")
    else:
        results = []
        failures = []

        with st.spinner(f"Analyzing {len(reviews)} review(s)..."):
            for index, review in enumerate(reviews, start=1):
                try:
                    response = requests.post(
                        API_URL,
                        json={"text": review},
                        timeout=REQUEST_TIMEOUT_SECONDS,
                    )
                    response.raise_for_status()
                    data = response.json()
                    results.append({
                        "review": review,
                        "label": data["label"],
                        "score": data["score"],
                        "theme": data["theme"],
                    })
                except requests.exceptions.RequestException as exc:
                    failures.append(f"Review {index}: API request failed ({exc})")
                    results.append({
                        "review": review,
                        "label": "error",
                        "score": 0,
                        "theme": "error",
                    })
                except (ValueError, KeyError, TypeError) as exc:
                    failures.append(f"Review {index}: unexpected API response ({exc})")
                    results.append({
                        "review": review,
                        "label": "error",
                        "score": 0,
                        "theme": "error",
                    })

        st.session_state.results = results
        st.session_state.analysis_failures = failures

if "results" in st.session_state:
    results = st.session_state.results
    failures = st.session_state.get("analysis_failures", [])

    if failures:
        st.warning(
            f"{len(failures)} review(s) could not be analyzed. "
            "Check that the FastAPI backend is deployed, its URL is correct, "
            "and GOOGLE_API_KEY is set on the backend service."
        )
        with st.expander("View API errors"):
            st.code("\n".join(failures))

    st.subheader("Results")
    st.dataframe(results, use_container_width=True)

    scores = [r["score"] for r in results if r["label"] != "error"]
    positive = [r for r in results if r["label"] == "positive"]
    themes = [r["theme"] for r in results if r["theme"] != "error"]

    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Reviews", len(results))
    if scores:
        col2.metric("Average score", round(sum(scores) / len(scores), 1))
        col3.metric("% Positive", f"{round(len(positive) / len(scores) * 100)}%")
    else:
        col2.metric("Average score", "—")
        col3.metric("% Positive", "—")

    if themes:
        top_theme = Counter(themes).most_common(1)[0][0]
        st.info(f"Customers talk most about: **{top_theme}**")

    if st.button("💾 Save to database"):
        save_results(results)
        st.success(f"Saved {len(results)} reviews to {DB_FILE}")

with st.expander("📚 Saved history (all reviews in the database)"):
    history = load_history()
    if history:
        st.write(f"Total saved so far: {len(history)}")
        st.dataframe(
            [{"review": r[0], "label": r[1], "score": r[2], "theme": r[3]} for r in history],
            use_container_width=True,
        )
    else:
        st.write("Nothing saved yet. Analyze some reviews and click Save.")
