# pages/quiz.py
import streamlit as st
from utils.database import DatabaseManager
from utils.adaptive_logic import AdaptiveEngine
import random
from config.settings import APP_CONFIG

db = DatabaseManager()
adaptive_engine = AdaptiveEngine()

def show():
    # your entire quiz logic here
    subjects = APP_CONFIG["subjects"]

    # If quiz hasn't started, show selection
    if "quiz_topic" not in st.session_state:
        subj = st.selectbox("Subject", list(subjects.keys()), key="quiz_subject_select")
        topic = st.selectbox("Topic", subjects[subj], key="quiz_topic_select")

        if st.button("Start Quiz"):
            st.session_state.quiz_topic = {"subject": subj, "topic": topic}
            st.session_state.quiz_topic_prev = {"subject": subj, "topic": topic}
            st.session_state.quiz_state = {}
            st.rerun()
        return  # Exit early until quiz starts

    # Quiz has started
    info = st.session_state.get("quiz_topic")
    if not info:
        st.info("Click 'Start Quiz' to begin.")
        return

    subj, topic = info["subject"], info["topic"]

    # Reset quiz state if subject/topic changed
    if (
        "quiz_topic_prev" not in st.session_state
        or st.session_state.quiz_topic != st.session_state.quiz_topic_prev
    ):
        st.session_state.quiz_state = {}
        st.session_state.quiz_topic_prev = st.session_state.quiz_topic

    level = db.get_user_topic_level(st.session_state.user_id, subj, topic)
    db.ensure_user_topic_entry(st.session_state.user_id, subj, topic, level)

    qs = st.session_state.quiz_state
    if not qs:
        st.session_state.quiz_state = {"n": 0, "correct": 0, "level": level, "q": None}
        qs = st.session_state.quiz_state

    # Hardcoded fallback question bank
    fallback_bank = {
        "Science": {
            "Chemistry": {
                1: [
                    {
                        "question": "Which of the following is a combustion reaction?",
                        "options": ["CH₄ + 2O₂ → CO₂ + 2H₂O", "HCl + NaOH → NaCl + H₂O", "AgNO₃ + NaCl → AgCl + NaNO₃", "Zn + HCl → ZnCl₂ + H₂"],
                        "correct_answer": "CH₄ + 2O₂ → CO₂ + 2H₂O",
                        "explanation": "Combustion reactions involve a substance reacting with oxygen to produce heat and light."
                    },
                    {
                        "question": "Which type of chemical reaction is represented by: 2H₂O₂ → 2H₂O + O₂?",
                        "options": ["Synthesis", "Decomposition", "Single displacement", "Combustion"],
                        "correct_answer": "Decomposition",
                        "explanation": "Hydrogen peroxide breaks down into water and oxygen — a classic decomposition reaction."
                    },
                    {
                        "question": "What do all acids release in aqueous solution?",
                        "options": ["OH⁻ ions", "H⁺ ions", "Na⁺ ions", "Cl⁻ ions"],
                        "correct_answer": "H⁺ ions",
                        "explanation": "Acids release hydrogen (H⁺) ions when dissolved in water."
                    },
                    {
                        "question": "Which substance is an element?",
                        "options": ["H₂", "HCl", "NaCl", "H₂O"],
                        "correct_answer": "H₂",
                        "explanation": "H₂ is a pure element made of two hydrogen atoms."
                    },
                    {
                        "question": "Which of the following is a physical change?",
                        "options": ["Boiling water", "Burning paper", "Rusting iron", "Baking a cake"],
                        "correct_answer": "Boiling water",
                        "explanation": "Boiling is a physical change as no new substance is formed."
                    },
                ],
                2: [
                    {
                        "question": "What type of chemical reaction is: 2KClO₃ → 2KCl + 3O₂?",
                        "options": ["Synthesis", "Decomposition", "Single Displacement", "Combustion"],
                        "correct_answer": "Decomposition",
                        "explanation": "One compound breaks down into simpler substances, characteristic of decomposition."
                    },
                    {
                        "question": "Which of the following is a sign that a chemical reaction has occurred?",
                        "options": ["Melting of ice", "Color change", "Breaking glass", "Boiling water"],
                        "correct_answer": "Color change",
                        "explanation": "Color change often indicates a new substance has formed during a chemical reaction."
                    },
                    {
                        "question": "Which metal is most reactive?",
                        "options": ["Gold", "Iron", "Potassium", "Copper"],
                        "correct_answer": "Potassium",
                        "explanation": "Potassium is highly reactive, especially with water."
                    },
                    {
                        "question": "What is the pH of a neutral solution?",
                        "options": ["7", "0", "14", "10"],
                        "correct_answer": "7",
                        "explanation": "A pH of 7 indicates a neutral solution like pure water."
                    },
                    {
                        "question": "Which gas is usually released during a metal-acid reaction?",
                        "options": ["Oxygen", "Carbon dioxide", "Hydrogen", "Nitrogen"],
                        "correct_answer": "Hydrogen",
                        "explanation": "Metals reacting with acids release hydrogen gas."
                    },
                ],
                3: [
                    {
                        "question": "Which of the following best represents a redox reaction?",
                        "options": ["H₂SO₄ + NaOH → Na₂SO₄ + H₂O", "AgNO₃ + NaCl → AgCl + NaNO₃", "2Fe + 3Cl₂ → 2FeCl₃", "CaCO₃ → CaO + CO₂"],
                        "correct_answer": "2Fe + 3Cl₂ → 2FeCl₃",
                        "explanation": "Iron is oxidized and chlorine is reduced — both oxidation and reduction occur."
                    },
                    {
                        "question": "Which process involves both oxidation and reduction?",
                        "options": ["Redox reaction", "Precipitation", "Neutralization", "Hydrolysis"],
                        "correct_answer": "Redox reaction",
                        "explanation": "Redox reactions involve simultaneous oxidation and reduction."
                    },
                    {
                        "question": "What is the oxidation number of hydrogen in most compounds?",
                        "options": ["+1", "0", "-1", "+2"],
                        "correct_answer": "+1",
                        "explanation": "Hydrogen usually has a +1 oxidation number in compounds."
                    },
                    {
                        "question": "Which indicator turns red in acid and blue in alkali?",
                        "options": ["Phenolphthalein", "Methyl orange", "Litmus", "Universal Indicator"],
                        "correct_answer": "Litmus",
                        "explanation": "Litmus is a common indicator: red in acid, blue in base."
                    },
                    {
                        "question": "Which element has the highest electronegativity?",
                        "options": ["Oxygen", "Chlorine", "Fluorine", "Nitrogen"],
                        "correct_answer": "Fluorine",
                        "explanation": "Fluorine is the most electronegative element."
                    },
                ]
            },
            "Biology": {
                1: [
                    {
                        "question": "What is the basic unit of heredity?",
                        "options": ["Cell", "Gene", "Chromosome", "Protein"],
                        "correct_answer": "Gene",
                        "explanation": "Genes are segments of DNA that carry hereditary information from parents to offspring."
                    },
                    {
                        "question": "Which of these is an example of a dominant trait?",
                        "options": ["Blue eyes", "Attached earlobes", "Widow's peak", "Straight hairline"],
                        "correct_answer": "Widow's peak",
                        "explanation": "Widow’s peak is a common example of a dominant trait passed from one generation to the next."
                    },
                    {
                        "question": "Where are genes located?",
                        "options": ["Cytoplasm", "Ribosomes", "Chromosomes", "Nucleus membrane"],
                        "correct_answer": "Chromosomes",
                        "explanation": "Genes are segments of DNA on chromosomes in the nucleus."
                    },
                    {
                        "question": "What does DNA stand for?",
                        "options": ["Deoxyribonucleic acid", "Deoxyribonuclear acid", "Dinucleic acid", "Dual nucleic acid"],
                        "correct_answer": "Deoxyribonucleic acid",
                        "explanation": "DNA is short for Deoxyribonucleic acid."
                    },
                    {
                        "question": "What determines the trait expressed by a gene?",
                        "options": ["The RNA sequence", "The environment", "The allele pair", "The cytoplasm"],
                        "correct_answer": "The allele pair",
                        "explanation": "Traits are determined by the combination of alleles (dominant/recessive)."
                    },
                ],
                2: [
                    {
                        "question": "In Mendel’s experiments, what was the ratio of dominant to recessive traits in the F2 generation?",
                        "options": ["1:1", "3:1", "9:3:3:1", "2:1"],
                        "correct_answer": "3:1",
                        "explanation": "In the F2 generation, Mendel observed a 3:1 ratio of dominant to recessive traits."
                    },
                    {
                        "question": "Which genotype represents a heterozygous individual?",
                        "options": ["AA", "aa", "Aa", "BB"],
                        "correct_answer": "Aa",
                        "explanation": "Heterozygous individuals have two different alleles for a trait, such as 'A' and 'a'."
                    },
                    {
                        "question": "What is a phenotype?",
                        "options": ["Genetic makeup", "Physical expression of traits", "Allele pair", "DNA sequence"],
                        "correct_answer": "Physical expression of traits",
                        "explanation": "Phenotype is how a trait appears based on genotype."
                    },
                    {
                        "question": "Which pair of chromosomes determines human sex?",
                        "options": ["1 and 2", "11 and 12", "X and Y", "A and B"],
                        "correct_answer": "X and Y",
                        "explanation": "The X and Y chromosomes determine biological sex."
                    },
                    {
                        "question": "Which of the following is *not* inherited genetically?",
                        "options": ["Eye color", "Blood type", "Language spoken", "Hair color"],
                        "correct_answer": "Language spoken",
                        "explanation": "Language is learned, not inherited through genes."
                    },
                ],
                3: [
                    {
                        "question": "A woman with blood type AB and a man with blood type O have a child. What are the possible blood types of the child?",
                        "options": ["A, B, AB, or O", "A or B", "AB only", "O only"],
                        "correct_answer": "A or B",
                        "explanation": "The AB parent contributes either A or B; the O parent contributes only O. So the child can be A or B."
                    },
                    {
                        "question": "In a dihybrid cross between two heterozygous individuals (RrYy × RrYy), what fraction of the offspring will show both recessive traits?",
                        "options": ["1/4", "1/8", "1/16", "9/16"],
                        "correct_answer": "1/16",
                        "explanation": "Only the offspring with the genotype rryy will express both recessive traits: 1 out of 16 combinations."
                    },
                    {
                        "question": "What is codominance?",
                        "options": ["One allele is dominant", "Both alleles are recessive", "Both alleles are expressed equally", "Neither allele is expressed"],
                        "correct_answer": "Both alleles are expressed equally",
                        "explanation": "In codominance, both traits appear in the phenotype."
                    },
                    {
                        "question": "Which disorder is caused by a single gene mutation?",
                        "options": ["Cancer", "Sickle Cell Anemia", "Diabetes", "Autism"],
                        "correct_answer": "Sickle Cell Anemia",
                        "explanation": "Sickle Cell is a well-known example of a single-gene mutation."
                    },
                    {
                        "question": "What is the chance of a carrier father and carrier mother having an affected child with a recessive condition?",
                        "options": ["25%", "50%", "75%", "100%"],
                        "correct_answer": "25%",
                        "explanation": "With both carriers, the chance is 1 in 4 (25%) for a recessive condition."
                    },
                ]
            }
        }
    }

    # Prevent displaying questions after 5
    if qs["n"] >= 5:
        if st.button("Finish"):
            acc = qs["correct"] / qs["n"] * 100
            st.success(f"🎉 You answered {qs['correct']} out of {qs['n']} correctly ({acc:.1f}%)!")

            with st.expander("📘 Review your answers"):
                for i, entry in enumerate(qs.get("history", []), 1):
                    st.markdown(f"**Q{i}:** {entry['question']}")
                    st.markdown(f"- Your answer: {entry['your_answer']}")
                    st.markdown(f"- Correct answer: {entry['correct_answer']}")
                    if entry["explanation"]:
                        st.markdown(f"_Explanation:_ {entry['explanation']}")
                    st.markdown("---")

            st.markdown("Here is your skill prediction, based on all previous attempts including the latest one.")
            show_skill_prediction()

            st.session_state.quiz_state = {}
        return

    # Get next question
    if qs["q"] is None:
        bank = fallback_bank.get(subj, {}).get(topic, {})
        level_questions = bank.get(min(qs["level"], 3), [])
        if qs["n"] < len(level_questions):
            qs["q"] = level_questions[qs["n"]]
        elif level_questions:
            qs["q"] = random.choice(level_questions)
        else:
            st.error("No questions available for this topic.")
            return

    # Show question
    q = qs["q"]
    st.subheader(f"{subj} – {topic}")
    st.write(f"**Q{qs['n'] + 1}:** {q['question']}")
    ans = st.radio("Answer:", q["options"], key=f"q_{qs['n']}")

    if st.button("Submit"):
        correct = (ans == q["correct_answer"])

        qs.setdefault("history", []).append({
            "question": q["question"],
            "your_answer": ans,
            "correct_answer": q["correct_answer"],
            "explanation": q.get("explanation", ""),
            "correct": correct
        })

        qs["n"] += 1
        if correct:
            qs["correct"] += 1

        db.record_quiz_answer(
            st.session_state.user_id,
            subj, topic,
            q["question"], ans, q["correct_answer"], correct,
            qs["level"]
        )
        qs["level"] = adaptive_engine.adjust_difficulty(qs["level"], correct, qs["n"], qs["correct"])
        qs["q"] = None
        st.rerun()

from utils.skill_predictor import SkillPredictor, get_prediction_summary
import pandas as pd

def show_skill_prediction():
    st.subheader("🧠 Predicted Skill Level")

    try:
        with st.spinner("🔄 Training model and predicting your skill level..."):
            predictor = SkillPredictor()
            predictor.process_datasets_and_train()

            test_df = pd.read_csv("utils/competency_v2_test.csv")
            predictions = predictor.predict(test_df)

            summary = get_prediction_summary(predictions)
        
        st.success("✅ Prediction complete!")
        st.markdown(summary)

    except Exception as e:
        st.error("⚠️ Failed to generate skill prediction.")
        st.exception(e)


