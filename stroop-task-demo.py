import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from st_keyup import st_keyup

# ==========================================
# 1. STIMULUS POOL CONFIGURATION
# ==========================================

COLORS = {
    "RED": "#FF0000",
    "BLUE": "#0066FF",
    "GREEN": "#00AA00",
    "YELLOW": "#E6B800"
}

TRIALS_PER_CONDITION = 20
ADMIN_PASSWORD = "backstreet"

# ==========================================
# 2. STROOP TRIAL GENERATOR
# ==========================================

def generate_stroop_schedule(trials_per_condition=20):
    """
    Generates a balanced Stroop schedule containing:
        - Congruent trials
        - Incongruent trials

    Returns:
        List[Dict]
    """

    trials = []

    color_words = list(COLORS.keys())

    # --------------------------
    # Congruent Trials
    # --------------------------
    for _ in range(trials_per_condition):
        word = random.choice(color_words)

        trials.append({
            "word": word,
            "font_color": word,
            "condition": "Congruent",
            "correct_response": word
        })

    # --------------------------
    # Incongruent Trials
    # --------------------------
    for _ in range(trials_per_condition):

        word = random.choice(color_words)

        possible_colors = [c for c in color_words if c != word]

        font_color = random.choice(possible_colors)

        trials.append({
            "word": word,
            "font_color": font_color,
            "condition": "Incongruent",
            "correct_response": font_color
        })

    random.shuffle(trials)

    return trials


# ==========================================
# 3. SESSION STATE INITIALIZATION
# ==========================================

st.set_page_config(
    page_title="Stroop Color Test",
    layout="centered"
)

st.markdown(
    """
    <div style="
        text-align:center;
        margin-top:15px;
        margin-bottom:15px;
        font-size:18px;
        color:#888;
    ">
        Press the key corresponding to the FONT COLOR.
    </div>
    """,
    unsafe_allow_html=True
)

if "stage" not in st.session_state:
    st.session_state.stage = "ready"

if "trials" not in st.session_state:
    st.session_state.trials = []

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

if "results" not in st.session_state:
    st.session_state.results = []

if "experiment_start_time" not in st.session_state:
    st.session_state.experiment_start_time = None

if "last_trial_time" not in st.session_state:
    st.session_state.last_trial_time = None

if "total_session_time" not in st.session_state:
    st.session_state.total_session_time = None

if "show_password_box" not in st.session_state:
    st.session_state.show_password_box = False


# ==========================================
# 4. TASK CONTROL FUNCTIONS
# ==========================================

def start_experiment():

    now = time.time()

    st.session_state.stage = "testing"
    st.session_state.experiment_start_time = now
    st.session_state.last_trial_time = now


def process_response(user_choice):

    now = time.time()

    idx = st.session_state.current_index

    current_trial = st.session_state.trials[idx]

    reaction_time = round(
        now - st.session_state.last_trial_time,
        4
    )

    st.session_state.last_trial_time = now

    correct_response = current_trial["correct_response"]

    is_correct = int(user_choice == correct_response)

    st.session_state.results.append({
        "trial_number": idx + 1,
        "word": current_trial["word"],
        "font_color": current_trial["font_color"],
        "condition": current_trial["condition"],
        "correct_response": correct_response,
        "user_response": user_choice,
        "is_correct": is_correct,
        "reaction_time_sec": reaction_time
    })

    if idx + 1 >= len(st.session_state.trials):

        st.session_state.stage = "completed"

        st.session_state.total_session_time = round(
            now - st.session_state.experiment_start_time,
            2
        )

    else:

        st.session_state.current_index += 1


# ==========================================
# 5. VIEW ROUTING
# ==========================================

# ------------------------------------------
# READY SCREEN
# ------------------------------------------

if st.session_state.stage == "ready":

    if not st.session_state.trials:
        st.session_state.trials = generate_stroop_schedule(
            TRIALS_PER_CONDITION
        )

    st.markdown(
        """
        <div style="text-align:center; margin-top:100px;">
            <h1 style="font-size:54px;">
                Stroop Color Test
            </h1>

            <p style="font-size:20px;">
                Select the FONT COLOR of the word.
            </p>

            <p>
                Ignore what the word says.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    _, c, _ = st.columns([1,1.2,1])

    with c:
        st.button(
            "Begin Test",
            use_container_width=True,
            on_click=start_experiment
        )

# ------------------------------------------
# ACTIVE TEST SCREEN
# ------------------------------------------

elif st.session_state.stage == "testing":

    idx = st.session_state.current_index

    trial = st.session_state.trials[idx]

    displayed_word = trial["word"]
    displayed_color = COLORS[trial["font_color"]]

    st.markdown(
        f"""
        <div style="text-align:center; margin-top:80px;">
            <p style="font-size:18px; color:#888;">
                What COLOR is this word displayed in?
            </p>

            <h1 style="
                font-size:90px;
                font-weight:800;
                color:{displayed_color};
                margin-top:20px;
            ">
                {displayed_word}
            </h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
    """
    <div style="
        text-align:center;
        margin-top:40px;
        color:#666;
    ">
        <p><b>Use Keyboard Responses</b></p>
        <p>R = RED | G = GREEN | B = BLUE | Y = YELLOW</p>
    </div>
    """,
    unsafe_allow_html=True
)

keyboard_input = st_keyup(
    "",
    key=f"keyboard_trial_{idx}",
    debounce=0
)

if keyboard_input:

    key_pressed = keyboard_input.strip().lower()

    if key_pressed == "r":
        process_response("RED")
        st.rerun()

    elif key_pressed == "g":
        process_response("GREEN")
        st.rerun()

    elif key_pressed == "b":
        process_response("BLUE")
        st.rerun()

    elif key_pressed == "y":
        process_response("YELLOW")
        st.rerun()

# ------------------------------------------
# COMPLETION SCREEN
# ------------------------------------------

elif st.session_state.stage == "completed":

    st.markdown(
        """
        <div style="text-align:center; margin-top:60px;">
            <h2>Task Complete</h2>
            <p>Thank you for participating.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not st.session_state.show_password_box:

        _, c, _ = st.columns([1,1,1])

        with c:

            if st.button(
                "Show Results",
                use_container_width=True
            ):
                st.session_state.show_password_box = True
                st.rerun()

    if st.session_state.show_password_box:

        password_input = st.text_input(
            "Enter Administrator Password:",
            type="password"
        )

        if password_input == ADMIN_PASSWORD:

            records = st.session_state.results

            total_trials = len(records)

            total_correct = sum(
                r["is_correct"]
                for r in records
            )

            accuracy = (
                100 * total_correct / total_trials
                if total_trials else 0
            )

            avg_rt = np.mean([
                r["reaction_time_sec"]
                for r in records
            ])

            congruent_trials = [
                r for r in records
                if r["condition"] == "Congruent"
            ]

            incongruent_trials = [
                r for r in records
                if r["condition"] == "Incongruent"
            ]

            congruent_rt = np.mean([
                r["reaction_time_sec"]
                for r in congruent_trials
            ])

            incongruent_rt = np.mean([
                r["reaction_time_sec"]
                for r in incongruent_trials
            ])

            stroop_effect = (
                incongruent_rt - congruent_rt
            )

            st.markdown("### Participant Summary")

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Accuracy",
                f"{accuracy:.1f}%"
            )

            c2.metric(
                "Avg RT",
                f"{avg_rt:.2f}s"
            )

            c3.metric(
                "Total Trials",
                total_trials
            )

            st.divider()

            st.markdown("### Stroop Metrics")

            s1, s2, s3 = st.columns(3)

            s1.metric(
                "Congruent RT",
                f"{congruent_rt:.2f}s"
            )

            s2.metric(
                "Incongruent RT",
                f"{incongruent_rt:.2f}s"
            )

            s3.metric(
                "Stroop Effect",
                f"{stroop_effect:.2f}s"
            )

            st.divider()

            df = pd.DataFrame(records)

            st.markdown(
                "### Trial-Level Results"
            )

            st.dataframe(
                df,
                use_container_width=True
            )

            csv = df.to_csv(index=False)

            st.download_button(
                "Download Results CSV",
                csv,
                "stroop_results.csv",
                "text/csv"
            )

            if st.button(
                "Reset Session for Next Participant"
            ):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]

                st.rerun()
