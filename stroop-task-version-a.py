import streamlit as st
import pandas as pd
import numpy as np
import time
import random

# ==========================================
# 1. STIMULUS POOL CONFIGURATION
# ==========================================

COLORS = {
    "RED": "#FF0000",
    "ORANGE": "#FF991C",
    "YELLOW": "#FFED29",
    "GREEN": "#00AA00",
    "BLUE": "#0066FF",
    "PINK": "#FF46A2"
}

TRIALS_PER_CONDITION = 24
ADMIN_PASSWORD = "backstreet"
SEED_MAP = {
    "A": 101,
    "B": 202,
    "C": 303
}
TEST_VERSION = "A"

# ==========================================
# 2. STROOP TRIAL GENERATOR
# ==========================================

def valid_schedule(trials):

    run_length = 1

    for i in range(1, len(trials)):

        if (
            trials[i]["correct_response"]
            ==
            trials[i - 1]["correct_response"]
        ):

            run_length += 1

            if run_length > 2:
                return False

        else:
            run_length = 1

    return True

def generate_stroop_schedule(
    trials_per_condition=24,
    seed=1
):

    random.seed(seed)
    trials = []
    color_words = list(COLORS.keys())
    color_pool = []

    for color in color_words:
        color_pool.extend(
            [color] * (trials_per_condition // len(color_words))
        )
    
    random.shuffle(color_pool)

    # --------------------------
    # Congruent Trials
    # --------------------------

    for word in color_pool:

        trials.append({
            "word": word,
            "font_color": word,
            "condition": "Congruent",
            "correct_response": word
        })

    # --------------------------
    # Incongruent Trials
    # --------------------------
    incongruent_pool = color_pool.copy()
    random.shuffle(incongruent_pool)

    for word in incongruent_pool:
    
        possible_colors = [
            c for c in color_words
            if c != word
        ]
    
        font_color = random.choice(possible_colors)

        trials.append({
            "word": word,
            "font_color": font_color,
            "condition": "Incongruent",
            "correct_response": font_color
        })

    for _ in range(1000):
    
        candidate = trials.copy()
    
        random.shuffle(candidate)
    
        if valid_schedule(candidate):
            return candidate
    
    return candidate


# ==========================================
# 3. SESSION STATE INITIALIZATION
# ==========================================

st.set_page_config(
    page_title="Stroop Test (Version A)",
    layout="centered"
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
# 4. TASK FUNCTIONS
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

    is_correct = int(
        user_choice == correct_response
    )

    st.session_state.results.append({

        "trial_number": idx + 1,

        "word": current_trial["word"],

        "display_color": current_trial["font_color"],

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
# SCREEN 1: READY
# ------------------------------------------

if st.session_state.stage == "ready":

    if not st.session_state.trials:

        st.session_state.trials = generate_stroop_schedule(
            TRIALS_PER_CONDITION,
            seed=SEED_MAP[TEST_VERSION]
        )

    st.markdown(
        """
        <div style="text-align:center; margin-top:100px;">
            <h1 style="font-size:54px;">
                Stroop Color Test
            </h1>
                Identify the FONT COLOR of each word, ignore what the word says.
            </p>
                Each color corresponds to a number on the keyboard.
            </p>
                Ex. Red = 1, Orange = 2, Yellow = 3
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    _, c, _ = st.columns([1, 1.2, 1])

    with c:

        st.button(
            "Click Here To Begin",
            use_container_width=True,
            on_click=start_experiment
        )


# ------------------------------------------
# SCREEN 2: TESTING
# ------------------------------------------

elif st.session_state.stage == "testing":

    idx = st.session_state.current_index

    trial = st.session_state.trials[idx]

    displayed_word = trial["word"]

    displayed_color = COLORS[
        trial["font_color"]
    ]

    st.markdown(
        """
        <div style="text-align:center;">
            <h3>
                What COLOR is this word displayed in?
            </h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Large stimulus presentation
    st.markdown(
        f"""
        <p style="
            text-align:center;
            color:{displayed_color};
            font-size:100px;
            font-weight:700;
            margin-top:80px;
            margin-bottom:80px;
        ">
        {displayed_word}
        </p>
        """,
        unsafe_allow_html=True
    )

    # Response Buttons

    col1, col2 = st.columns(2)

    with col1:

        st.button(
            "RED - PRESS", 
            shortcut="1",
            use_container_width=True,
            on_click=process_response,
            args=("RED",)
        )

        st.button(
            "ORANGE - PRESS",
            shortcut="2",
            use_container_width=True,
            on_click=process_response,
            args=("ORANGE",)
        )

        st.button(
            "YELLOW - PRESS",
            shortcut="3",
            use_container_width=True,
            on_click=process_response,
            args=("YELLOW",)
        )

    with col2:

        st.button(
            "GREEN - PRESS",
            shortcut="4",
            use_container_width=True,
            on_click=process_response,
            args=("GREEN",)
        )

        st.button(
            "BLUE - PRESS",
            shortcut="5",
            use_container_width=True,
            on_click=process_response,
            args=("BLUE",)
        )

        st.button(
            "PINK - PRESS",
            shortcut="6",
            use_container_width=True,
            on_click=process_response,
            args=("PINK",)
        )


# ------------------------------------------
# SCREEN 3: COMPLETED
# ------------------------------------------

elif st.session_state.stage == "completed":

    st.markdown(
        f"""
        <div style="text-align:center; margin-top:60px;">
            <h2>Task Complete</h2>
                Thank you for your participation!
        </div>
        """,
        unsafe_allow_html=True
    )

    if not st.session_state.show_password_box:

        _, c, _ = st.columns([1, 1, 1])

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
                total_correct / total_trials * 100
                if total_trials > 0
                else 0
            )

            avg_rt = np.mean(
                [r["reaction_time_sec"] for r in records]
            )

            congruent_trials = [
                r for r in records
                if r["condition"] == "Congruent"
            ]

            incongruent_trials = [
                r for r in records
                if r["condition"] == "Incongruent"
            ]

            congruent_rt = np.mean(
                [r["reaction_time_sec"]
                 for r in congruent_trials]
            )

            incongruent_rt = np.mean(
                [r["reaction_time_sec"]
                 for r in incongruent_trials]
            )

            stroop_effect = (
                incongruent_rt - congruent_rt
            )

            st.markdown("### Participant Summary")

            m1, m2, m3, m4 = st.columns(4)

            m1.metric(
                "Accuracy",
                f"{accuracy:.1f}%"
            )

            m2.metric(
                "Average RT",
                f"{avg_rt:.2f}s"
            )

            m3.metric(
                "Total Trials",
                total_trials
            )

            m4.metric(
                "Completion Time",
                f"{st.session_state.total_session_time:.2f}s"
            )

            st.divider()

            st.markdown(
                "### Stroop Effect Metrics"
            )

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

            summary_data = {
                "Total Trials": total_trials,
                "Total Correct": total_correct,
                "Accuracy (%)": round(accuracy, 2),
                "Average RT (s)": round(avg_rt, 3),
                "Congruent RT (s)": round(congruent_rt, 3),
                "Incongruent RT (s)": round(incongruent_rt, 3),
                "Stroop Effect (s)": round(stroop_effect, 3),
                "Completion Time (s)": round(
                    st.session_state.total_session_time,
                    2
                )
            }

            summary_df = pd.DataFrame(
                summary_data.items(),
                columns=["Metric", "Value"]
            )

            st.divider()

            st.markdown(
                "### Overall Session Statistics"
            )

            st.dataframe(
                summary_df,
                use_container_width=True
            )

            df = pd.DataFrame(records)

            st.divider()

            st.markdown(
                "### Trial-Level Results"
            )

            st.dataframe(
                df,
                use_container_width=True
            )

            csv_data = (
                summary_df.to_csv(index=False)
                + "\n"
                + df.to_csv(index=False)
            )

            st.download_button(
                "Download Results CSV",
                csv_data,
                "stroop_results.csv",
                "text/csv"
            )

            if st.button(
                "Reset Session for Next Participant"
            ):

                for key in list(
                    st.session_state.keys()
                ):
                    del st.session_state[key]

                st.rerun()
