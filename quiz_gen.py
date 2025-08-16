
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage


# llm = ChatGoogleGenerativeAI(google_api_key="AIzaSyC5WzZt5eqtvwxoVl1ec6dXxkHDloeVFaM",model="gemini-1.5-flash", temperature=0.7)

# res = llm.invoke([
#     SystemMessage(content="You are a helpful assistant."),
#     HumanMessage(content="Translate 'Hello' to French.")
# ])

# print(res.content)



def quiz_gen(text):

    def chunk_text(text, chunk_size, overlap=0):
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk = words[i:i+chunk_size]
            chunks.append(' '.join(chunk))
            i += chunk_size - overlap  # overlap
        return chunks
    size = int(len(text.split()) / 5)
    chunks = chunk_text(text,size)
    print(f"Number of chunks: {len(chunks)}")
    if len(chunks) > 5:
        chunks = chunks[:5]
    print(chunks[4])

    # Merge all chunks into one
    merged_text = "\n".join(chunks)
    SAFE_TOKEN_LIMIT = 100000  # well below Gemini's max for reliability
    TOTAL_QUESTIONS = 15       # final total questions

    import tiktoken
    # ------------------ TOKEN COUNTING ------------------ #
    def count_tokens(text):
        enc = tiktoken.get_encoding("cl100k_base")  # works well for estimation
        return len(enc.encode(text))

    merged_tokens = count_tokens(merged_text)
    print(f"Merged text token count: {merged_tokens}")

    # ------------------ SAFE SPLITTING ------------------ #
    if merged_tokens > SAFE_TOKEN_LIMIT:
        print("⚠️ Text too large — splitting into multiple safe sections.")
        num_sections = (merged_tokens // SAFE_TOKEN_LIMIT) + 1
        words_per_section = len(merged_text.split()) // num_sections
        safe_sections = chunk_text(merged_text, words_per_section, overlap=0)
    else:
        safe_sections = [merged_text]

    # ------------------ PROMPTS ------------------ #
    def get_quiz_prompt(text, num_questions):
        return f"""
    You are a quiz generation assistant.
    Read the following text and create exactly {num_questions} multiple-choice questions:
    Given the lecture or Doc text, extract ONLY important questions that test key concepts, definitions, processes, or cause-effect relationships.
    Ignore unimportant details, filler words, or trivial examples.


    - Split: beginner, medium, hard.
    - Beginner: easy recall (40% of the Questions)
    - Medium: moderate reasoning (40% of the Questions)
    - Hard: deeper understanding (20% of the Questions)

    Rules:
    1. Each question must have:
    - "question": The question text
    - "options": Exactly 4 options labeled A), B), C), D)
    - "correct": The correct option letter only (A/B/C/D)
    2. Strictly output ONLY a JSON list, like:
    [
        {{
            "question": "....?",
            "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
            "correct": "B"
        }},
        ...
    ]
    3. Avoid vague or nonsensical questions.
    4. Each question must be clear and unambiguous.
    5. Avoid repeating the same idea.



    Text:
    \"\"\"{text}\"\"\"
    """
    review_prompt = """
    You are a quiz reviewer and fixer.
    You will receive the raw output from a quiz generation agent, which *should* be a JSON list of quiz questions.
    Your job is to:
    - Extract the valid JSON list from the provided text, ignoring any surrounding non-JSON content.
    - Ensure the extracted JSON is valid and well-formatted.
    - Ensure each question makes sense and is related to the provided text.
    - Ensure each question has exactly 4 options labeled A), B), C), D).
    - Ensure "correct" contains only one letter (A/B/C/D) and matches one of the options.
    If there are issues with the JSON structure or content, correct them. Output ONLY the fixed JSON list.
    """

    # ------------------ AGENTS ------------------ #
    from crewai import Agent, Task, Crew
    import os
    os.environ["GEMINI_API_KEY"] = "AIzaSyDwu1LUYKCXGnwon-Z6zjUPNtANqes8Ujc"

    quiz_generator = Agent(
        role="Quiz Generator",
        goal="Generate a valid JSON quiz from text.",
        backstory="Expert in educational quiz creation with difficulty variety.",
        allow_delegation=False,
        llm="gemini/gemini-1.5-flash", # Assuming llm is already initialized with provider
    )

    quiz_reviewer = Agent(
        role="Quiz Reviewer",
        goal="Review and fix quiz JSON to ensure format and logic correctness.",
        backstory="Expert in content review, JSON validation, and education.",
        allow_delegation=False,
        llm="gemini/gemini-1.5-flash", # Assuming llm is already initialized with provider
    )

    # ------------------ GENERATION LOOP ------------------ #
    import json
    import re

    def extract_json_from_result(result):
        # Try to find a ```json block``` first
        cleaned = re.search(r"```json\s*(.*?)```", result, re.DOTALL)
        if cleaned:
            json_text = cleaned.group(1)
        return json_text.strip()


    all_questions = []
    questions_per_section = TOTAL_QUESTIONS // len(safe_sections)

    for section in safe_sections:
        generate_task = Task(
            description=get_quiz_prompt(section, questions_per_section),
            expected_output="A JSON list of quiz questions in the required format.",
            agent=quiz_generator
        )

        crew_gen = Crew(
            agents=[quiz_generator],
            tasks=[generate_task],
            verbose=False
        )

        result_obj = crew_gen.kickoff()

        # CrewOutput usually has a .raw or .outputs property — let's extract the text
        if hasattr(result_obj, "raw"):
            result = result_obj.raw
        elif hasattr(result_obj, "outputs"):
            # If it's a dict-like output
            result = result_obj.outputs.get("output") or str(result_obj.outputs)
        else:
            result = str(result_obj)
        print(result)

        json_text = extract_json_from_result(result)

        try:
            questions = json.loads(json_text)
            if isinstance(questions, list) and all("question" in q and "options" in q and "correct" in q for q in questions):
                all_questions.extend(questions)

            else:
                raise ValueError("Invalid structure")
        except Exception:
            print("  ")

    # ------------------ FINAL REVIEW ------------------ #
    print(all_questions)
    print(json_text)

    review_task = Task(
        description=review_prompt + "\n\nHere is the quiz to review:\n" + json.dumps(all_questions, ensure_ascii=False, indent=2),
        expected_output="A corrected JSON list of quiz questions.",
        agent=quiz_reviewer
    )

    crew_review = Crew(
        agents=[quiz_reviewer],
        tasks=[review_task],
        verbose=True
    )

    final_result = crew_review.kickoff()

    import random
    import json
    import re

    # Ensure final_result is plain text
    if hasattr(final_result, "raw"):
        final_result = final_result.raw
    elif hasattr(final_result, "output_text"):
        final_result = final_result.output_text
    else:
        final_result = str(final_result)  # fallback

    try:
        # Optional: extract JSON if wrapped in ```json ... ```
        cleaned = re.search(r"```json\s*(.*?)```", final_result, re.DOTALL)
        json_text = cleaned.group(1) if cleaned else final_result
        quiz_data = json.loads(json_text)

        # Shuffle questions so difficulties are mixed
        random.shuffle(quiz_data)

        # ✅ Instead of saving, return JSON
        return quiz_data  

    except json.JSONDecodeError:
        print("❌ Final output is not valid JSON.")
        return []