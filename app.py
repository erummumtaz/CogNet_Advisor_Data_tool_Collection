import streamlit as st
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ============================================================
# FSLSM QUESTION BANK (44 items - COMPLETE)
# ============================================================

FSLSM_QUESTIONS = [
    ("I understand something better after I (a) try it out. (b) think it through.", "ACT_REF", "a"),
    ("I would rather be considered (a) realistic. (b) innovative.", "SEN_INT", "a"),
    ("When I think about what I did yesterday, I am most likely to get (a) a picture. (b) words.", "VIS_VER", "a"),
    ("I tend to (a) understand details of a subject but may be fuzzy about its overall structure. (b) understand the overall structure but may be fuzzy about details.", "SEQ_GLO", "a"),
    ("When I am learning something new, it helps me to (a) talk about it. (b) think about it.", "ACT_REF", "a"),
    ("If I were a teacher, I would rather teach a course (a) that deals with facts and real life situations. (b) that deals with ideas and theories.", "SEN_INT", "a"),
    ("I prefer to get new information in (a) pictures, diagrams, graphs, or maps. (b) written directions or verbal information.", "VIS_VER", "a"),
    ("Once I understand (a) all the parts, I understand the whole thing. (b) the whole thing, I see how the parts fit.", "SEQ_GLO", "a"),
    ("In a study group working on difficult material, I am more likely to (a) jump in and contribute ideas. (b) sit back and listen.", "ACT_REF", "a"),
    ("I find it easier (a) to learn facts. (b) to learn concepts.", "SEN_INT", "a"),
    ("In a book with lots of pictures and charts, I am likely to (a) look over the pictures and charts carefully. (b) focus on the written text.", "VIS_VER", "a"),
    ("When I solve math problems (a) I usually work my way to the solutions one step at a time. (b) I often just see the solutions but then have to struggle to figure out the steps to get to them.", "SEQ_GLO", "a"),
    ("In classes I have taken (a) I have usually gotten to know many of the students. (b) I have rarely gotten to know many of the students.", "ACT_REF", "a"),
    ("In reading nonfiction, I prefer (a) something that teaches me new facts or tells me how to do something. (b) something that gives me new ideas to think about.", "SEN_INT", "a"),
    ("I like teachers (a) who put a lot of diagrams on the board. (b) who spend a lot of time explaining.", "VIS_VER", "a"),
    ("When I'm analyzing a story or a novel (a) I think of the incidents and try to put them together to figure out the themes. (b) I just know what the themes are when I finish reading and then I have to go back and find the incidents that demonstrate them.", "SEQ_GLO", "a"),
    ("When I start a homework problem, I am more likely to (a) start working on the solution immediately. (b) try to fully understand the problem first.", "ACT_REF", "a"),
    ("I prefer the idea of (a) certainty. (b) theory.", "SEN_INT", "a"),
    ("I remember best (a) what I see. (b) what I hear.", "VIS_VER", "a"),
    ("It is more important to me that an instructor (a) lay out the material in clear sequential steps. (b) give me an overall picture and relate the material to other subjects.", "SEQ_GLO", "a"),
    ("I prefer to study (a) in a study group. (b) alone.", "ACT_REF", "a"),
    ("I am more likely to be considered (a) careful about the details of my work. (b) creative about how to do my work.", "SEN_INT", "a"),
    ("When I get directions to a new place, I prefer (a) a map. (b) written instructions.", "VIS_VER", "a"),
    ("I learn (a) at a fairly regular pace. If I study hard, I'll 'get it.' (b) in fits and starts. I'll be totally confused and then suddenly it all 'clicks.'", "SEQ_GLO", "a"),
    ("I would rather first (a) try things out. (b) think about how I'm going to do it.", "ACT_REF", "a"),
    ("When I am reading for enjoyment, I like writers to (a) clearly say what they mean. (b) say things in creative, interesting ways.", "SEN_INT", "a"),
    ("When I see a diagram or sketch in class, I am most likely to remember (a) the picture. (b) what the instructor said about it.", "VIS_VER", "a"),
    ("When considering a body of information, I am more likely to (a) focus on details and miss the big picture. (b) try to understand the big picture before getting into the details.", "SEQ_GLO", "a"),
    ("I more easily remember (a) something I have done. (b) something I have thought a lot about.", "ACT_REF", "a"),
    ("When I have to perform a task, I prefer to (a) master one way of doing it. (b) come up with new ways of doing it.", "SEN_INT", "a"),
    ("When someone is showing me data, I prefer (a) charts or graphs. (b) text summarizing the results.", "VIS_VER", "a"),
    ("When writing a paper, I am more likely to (a) work on (think about or write) the beginning of the paper and progress forward. (b) work on (think about or write) different parts of the paper and then order them.", "SEQ_GLO", "a"),
    ("When I have to work on a group project, I first want to (a) have 'group brainstorming' where everyone contributes ideas. (b) brainstorm individually and then come together as a group to compare ideas.", "ACT_REF", "a"),
    ("I consider it higher praise to call someone (a) sensible. (b) imaginative.", "SEN_INT", "a"),
    ("When I meet people at a party, I am more likely to remember (a) what they looked like. (b) what they said about themselves.", "VIS_VER", "a"),
    ("When I am learning a new subject, I prefer to (a) stay focused on that subject, learning as much about it as I can. (b) try to make connections between that subject and related subjects.", "SEQ_GLO", "a"),
    ("I am more likely to be considered (a) outgoing. (b) reserved.", "ACT_REF", "a"),
    ("I prefer courses that emphasize (a) concrete material (facts, data). (b) abstract material (concepts, theories).", "SEN_INT", "a"),
    ("For entertainment, I would rather (a) watch television. (b) read a book.", "VIS_VER", "a"),
    ("Some teachers start their lectures with an outline of what they will cover. Such outlines are (a) somewhat helpful to me. (b) very helpful to me.", "SEQ_GLO", "a"),
    ("The idea of doing homework in groups, with one grade for the entire group, (a) appeals to me. (b) does not appeal to me.", "ACT_REF", "a"),
    ("When I am doing long calculations, (a) I tend to repeat all my steps and check my work carefully. (b) I find checking my work tiresome and have to force myself to do it.", "SEQ_GLO", "a"),
    ("I tend to picture places I have been (a) easily and fairly accurately. (b) with difficulty and without much detail.", "VIS_VER", "a"),
    ("When solving problems in a group, I would be more likely to (a) think of the steps in the solution process. (b) think of possible consequences or applications of the solution in a wide range of areas.", "SEQ_GLO", "a"),
]


def compute_profile(answers):
    """Compute FSLSM profile scores from (dim, delta) answers."""
    scores = {"ACT_REF": 0, "SEN_INT": 0, "VIS_VER": 0, "SEQ_GLO": 0}
    for dim, delta in answers:
        scores[dim] += delta

    visual = max(0.0, min(1.0, (scores["VIS_VER"] + 11) / 22.0))
    sensing = max(0.0, min(1.0, (scores["SEN_INT"] + 11) / 22.0))
    active = max(0.0, min(1.0, (scores["ACT_REF"] + 11) / 22.0))
    global_score = max(0.0, min(1.0, (scores["SEQ_GLO"] + 11) / 22.0))

    return {
        "visual": visual,
        "sensing": sensing,
        "active": active,
        "global": global_score
    }


def check_duplicate(student_id, course_name):
    """Check if this student has already submitted this course."""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        if "google_credentials" in st.secrets:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_credentials"], scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

        client = gspread.authorize(creds)
        sheet = client.open("CogNet_Advisory_Data").sheet1
        records = sheet.get_all_values()

        if len(records) <= 1:
            return False

        for row in records[1:]:
            if len(row) > 6:
                if row[1].strip().lower() == student_id.strip().lower() and row[6].strip().lower() == course_name.strip().lower():
                    return True
        return False
    except Exception as e:
        st.error(f"Duplicate check failed: {e}")
        return False


def convert_grade(grade_input, grade_format):
    """Convert grade to 0-1 scale."""
    if grade_format == "4.0 GPA Scale":
        return grade_input / 4.0
    elif grade_format == "Percentage (0-100%)":
        return grade_input / 100.0
    elif grade_format == "Letter Grade (A, B, C, etc.)":
        letter_map = {
            'A+': 4.0, 'A': 4.0, 'A-': 3.7,
            'B+': 3.3, 'B': 3.0, 'B-': 2.7,
            'C+': 2.3, 'C': 2.0, 'C-': 1.7,
            'D+': 1.3, 'D': 1.0, 'D-': 0.7,
            'F': 0.0
        }
        letter = grade_input.strip().upper()
        if letter in letter_map:
            return letter_map[letter] / 4.0
        else:
            st.error(f"Unknown letter grade: {grade_input}. Please use A, B, C, etc.")
            return 0.0
    else:
        return 0.0


def save_to_gsheet(student_data):
    """Save student data to Google Sheets with headers."""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        if "google_credentials" in st.secrets:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_credentials"], scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

        client = gspread.authorize(creds)
        sheet = client.open("CogNet_Advisory_Data").sheet1

        # Check if sheet is empty (no headers)
        records = sheet.get_all_values()
        if len(records) == 0:
            # Write headers
            headers = [
                "Timestamp", "Student_ID", "University", "Degree", "Year",
                "GPA", "Course_Taken", "Visual", "Sensing", "Active", "Global",
                "C_vis_Perceived", "C_prac_Perceived", "C_struct_Perceived",
                "Final_Grade"
            ]
            sheet.append_row(headers)

        # Write data row
        row = [
            datetime.datetime.now().isoformat(),
            student_data["name"],
            student_data["university"],
            student_data["degree"],
            student_data["year"],
            student_data["gpa"],
            student_data["course_taken"],
            student_data["visual"],
            student_data["sensing"],
            student_data["active"],
            student_data["global"],
            student_data.get("c_vis", 0.0),
            student_data.get("c_prac", 0.0),
            student_data.get("c_struct", 0.0),
            student_data.get("final_grade", 0.0)
        ]
        sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"Error saving to Google Sheets: {e}")
        return False


# ============================================================
# STREAMLIT MAIN APP
# ============================================================

st.set_page_config(page_title="CogNet Advisor - Data Collection", layout="wide")
st.title("CogNet Advisor")
st.markdown("*Learning Style Assessment for Course Recommendation Research*")

st.info("""
This survey collects your learning preferences (FSLSM) and academic background.
Your responses are anonymous and will only be used for research purposes.
""")

# --- Student Information Form ---
st.subheader("Academic Background")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Student Name / Unique ID", placeholder="e.g., Student_001")
    university = st.text_input("University / Institute")
    degree = st.text_input("Degree Program", placeholder="e.g., BS Computer Science")
with col2:
    year = st.selectbox("Academic Year", [1, 2, 3, 4, 5, "MS", "PhD"])
    gpa = st.number_input("Cumulative GPA (on a 4.0 scale)", min_value=0.0, max_value=4.0, step=0.01)
    course_taken = st.text_input("Course Name", placeholder="e.g., Artificial Intelligence")

# --- Course Content Rating ---
st.subheader("Course Content Assessment")
st.caption("Rate the course you took/are taking on the following aspects. This helps us understand the course characteristics.")

col_rating1, col_rating2, col_rating3 = st.columns(3)

with col_rating1:
    st.markdown("**Visual Content**")
    st.caption("Diagrams, charts, images, animations")
    c_vis_raw = st.slider(
        "Visual Content (%)",
        min_value=0,
        max_value=100,
        value=50,
        step=5,
        key="c_vis_slider"
    )
    c_vis = c_vis_raw / 100.0
    st.caption(f"Normalized: {c_vis:.2f}")

with col_rating2:
    st.markdown("**Practical Content**")
    st.caption("Hands-on, lab, programming, projects")
    c_prac_raw = st.slider(
        "Practical Content (%)",
        min_value=0,
        max_value=100,
        value=50,
        step=5,
        key="c_prac_slider"
    )
    c_prac = c_prac_raw / 100.0
    st.caption(f"Normalized: {c_prac:.2f}")

with col_rating3:
    st.markdown("**Structure/Organization**")
    st.caption("Clear weekly plan, learning objectives")
    c_struct_raw = st.slider(
        "Structure/Organization (%)",
        min_value=0,
        max_value=100,
        value=50,
        step=5,
        key="c_struct_slider"
    )
    c_struct = c_struct_raw / 100.0
    st.caption(f"Normalized: {c_struct:.2f}")

# --- Final Grade (Mandatory - Default 0.00) ---
st.subheader("Final Grade")
st.caption("Please enter your grade in one of the formats below. If your semester has not ended, enter 0.00.")

grade_format = st.selectbox(
    "Select your grade format:",
    ["Percentage (0-100%)", "4.0 GPA Scale", "Letter Grade (A, B, C, etc.)"],
    key="grade_format"
)

# Initialize variables
grade_input = None
normalized_grade = 0.0

if grade_format == "4.0 GPA Scale":
    grade_input = st.number_input(
        "Your GPA (0.00 - 4.00)",
        min_value=0.0,
        max_value=4.0,
        step=0.01,
        value=0.0
    )
    normalized_grade = grade_input / 4.0
    if grade_input > 0:
        st.success(f"Your grade has been converted to: **{normalized_grade:.3f}** (0-1 scale)")
    else:
        st.info("Enter 0.00 if the semester has not ended yet.")

elif grade_format == "Percentage (0-100%)":
    grade_input = st.number_input(
        "Your Percentage (0 - 100)",
        min_value=0.0,
        max_value=100.0,
        step=0.5,
        value=0.0
    )
    normalized_grade = grade_input / 100.0
    if grade_input > 0:
        st.success(f"Your grade has been converted to: **{normalized_grade:.3f}** (0-1 scale)")
    else:
        st.info("Enter 0.00 if the semester has not ended yet.")

else:  # Letter Grade
    grade_input = st.text_input(
        "Your Letter Grade",
        placeholder="e.g., A, B+, C-",
        value=""
    )
    if grade_input:
        normalized_grade = convert_grade(grade_input, grade_format)
        if normalized_grade > 0:
            st.success(f"Your grade has been converted to: **{normalized_grade:.3f}** (0-1 scale)")
        else:
            st.warning("Please enter a valid letter grade (e.g., A, B+, C-).")
    else:
        normalized_grade = 0.0
        st.info("Leave empty if the semester has not ended yet.")

if not name or not course_taken:
    st.warning("Please enter your Student ID and Course Name to proceed.")
    st.stop()

# --- FSLSM Assessment (All 44 Questions on One Page) ---
st.subheader("Learning Style Preferences (44 Questions)")
st.markdown("Please answer all questions. Choose the option **(a)** or **(b)** that best describes you.")

# Initialize session state for answers
if "answers" not in st.session_state:
    st.session_state.answers = []
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "profile" not in st.session_state:
    st.session_state.profile = None

if st.session_state.submitted:
    st.success("You have already submitted your responses for this course. Thank you!")
    st.stop()

# Display all questions
answers = []
for i, (q_text, dim, pole) in enumerate(FSLSM_QUESTIONS):
    clean_q = q_text.replace("(a)", "").replace("(b)", "").strip()
    parts = q_text.split("(a)")[1].split("(b)")
    choice_a = "(a) " + parts[0].strip()
    choice_b = "(b) " + parts[1].strip()
    
    # Use a unique key for each question
    choice = st.radio(
        f"**Question {i+1}. {clean_q}**",
        [choice_a, choice_b],
        key=f"q_{i}",
        index=None
    )
    answers.append(choice)

# Check if all questions are answered
all_answered = all(a is not None for a in answers)

if not all_answered:
    st.warning("Please answer all 44 questions before submitting.")
else:
    # Compute profile
    profile_answers = []
    for i, (q_text, dim, pole) in enumerate(FSLSM_QUESTIONS):
        choice = answers[i]
        selected = "a" if choice.startswith("(a)") else "b"
        delta = 1 if selected == pole else -1
        profile_answers.append((dim, delta))
    
    profile = compute_profile(profile_answers)
    st.session_state.profile = profile

    st.markdown("---")
    st.subheader("Your Learning Profile")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Visual", f"{profile['visual']:.3f}")
    col2.metric("Sensing", f"{profile['sensing']:.3f}")
    col3.metric("Active", f"{profile['active']:.3f}")
    col4.metric("Global", f"{profile['global']:.3f}")
    st.caption("Higher scores indicate a stronger preference for that learning style.")
    st.markdown("---")

    # --- Submit to Google Sheets ---
    student_data = {
        "name": name,
        "university": university,
        "degree": degree,
        "year": year,
        "gpa": gpa,
        "course_taken": course_taken,
        "visual": profile['visual'],
        "sensing": profile['sensing'],
        "active": profile['active'],
        "global": profile['global'],
        "c_vis": c_vis,
        "c_prac": c_prac,
        "c_struct": c_struct,
        "final_grade": normalized_grade
    }

    # Show summary before submission
    with st.expander("Review Your Responses Before Submitting"):
        st.write("**Course Ratings:**")
        st.write(f"- Visual Content: {c_vis_raw}% → Normalized: {c_vis:.2f}")
        st.write(f"- Practical Content: {c_prac_raw}% → Normalized: {c_prac:.2f}")
        st.write(f"- Structure/Organization: {c_struct_raw}% → Normalized: {c_struct:.2f}")
        st.write(f"- Final Grade: {normalized_grade:.3f} (0-1 scale)")

    if st.button("Submit Response", type="primary"):
        if check_duplicate(name, course_taken):
            st.error(f"You have already submitted a response for '{course_taken}' under {name}. Please select a different course for this submission.")
            st.info("If you are taking multiple courses, complete this survey separately for each course.")
        else:
            if save_to_gsheet(student_data):
                st.session_state.submitted = True
                st.success("Your responses have been saved successfully. Thank you for contributing to our research!")
            else:
                st.error("Failed to save. Please ensure Google Sheets setup is correct.")

    # Allow CSV download for local backup
    if st.button("Download CSV (Local Backup)"):
        import pandas as pd
        df = pd.DataFrame([student_data])
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV File",
            data=csv,
            file_name="my_fslsm_profile.csv",
            mime="text/csv"
        )
