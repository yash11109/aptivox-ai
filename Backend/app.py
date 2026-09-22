import os
import sys
import random
import time
import io
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS

# File parsing imports
try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import docx
except ImportError:
    docx = None

# Add Database and Backend paths
backend_dir = Path(__file__).resolve().parent
project_root = backend_dir.parent
db_dir = project_root / "Database"
frontend_dir = project_root / "Frontend"

if str(db_dir) not in sys.path:
    sys.path.insert(0, str(db_dir))

from config import Config
from database import db_manager

app = Flask(
    __name__,
    template_folder=str(frontend_dir / "templates"),
    static_folder=str(frontend_dir / "static")
)
app.config.from_object(Config)
CORS(app)

# Initialize Hybrid Database Manager
db_manager.init_app(app)

# Basic Question Library across all languages and technical categories
AI_QUESTION_POOL = {
    "HTML": [
        {
            "id": "gen_h1",
            "question": "What is HTML?",
            "hint": "Explain what the acronym stands for, its primary role in web development, and how it provides structure to web pages.",
            "star_guide": "S: Starting web development. T: Explain web fundamentals. A: Defined HyperText Markup Language as the foundational markup that structures web documents. R: Solid foundation for web pages.",
            "sample_answer": "HTML stands for HyperText Markup Language. It is the standard markup language used to create and structure web pages on the internet. It uses elements and tags (such as headings, paragraphs, links, and images) to tell web browsers how to display text and media content."
        },
        {
            "id": "gen_h2",
            "question": "What is the difference between an HTML tag and an HTML element?",
            "hint": "Compare opening/closing tags like <p> and </p> with the full element including content.",
            "star_guide": "S: Code review on semantic markup. T: Explain terminology. A: Clarified that tags are syntax markers and elements are the complete unit including tags and inner content. R: Improved developer terminology.",
            "sample_answer": "An HTML tag is the syntax marker enclosed in angle brackets used to mark the start or end of an element (such as <p> and </p>). An HTML element is the complete unit, consisting of the opening tag, any attributes, the enclosed content, and the closing tag."
        },
        {
            "id": "gen_h3",
            "question": "What are HTML attributes and why are they used?",
            "hint": "Mention href, src, id, class, and their placement inside opening tags.",
            "star_guide": "S: Configuring element behavior. T: Apply attributes to HTML tags. A: Used attributes like class, id, and href to configure links and styling hooks. R: Seamless integration between HTML, CSS, and JS.",
            "sample_answer": "HTML attributes provide additional information and properties to HTML elements. They are placed inside the opening tag as name-value pairs (e.g., class='card', href='https://...', or id='header') to specify styling hooks, image sources, or behavioral metadata."
        }
    ],
    "CSS": [
        {
            "id": "gen_c1",
            "question": "What is CSS?",
            "hint": "Explain what CSS stands for and its role in styling colors, layouts, typography, and visual presentation.",
            "star_guide": "S: Styling a web application. T: Separate structure from design. A: Implemented CSS stylesheets for visual styling, responsive layouts, and typography. R: Created an attractive, modern user interface.",
            "sample_answer": "CSS stands for Cascading Style Sheets. It is a stylesheet language used to describe the visual presentation and layout of an HTML document. CSS controls colors, fonts, margins, layouts, animations, and responsive designs across different device screens."
        },
        {
            "id": "gen_c2",
            "question": "What is the CSS Box Model and what are its four parts?",
            "hint": "Mention Content, Padding, Border, and Margin from inside to outside.",
            "star_guide": "S: Fixing spacing and layout overflow. T: Master component sizing. A: Applied the CSS box model correctly using box-sizing: border-box. R: Predictable layout sizing across all components.",
            "sample_answer": "The CSS Box Model is a core concept that defines how every HTML element is represented as a rectangular box. It consists of four layers from inside out: 1) Content (the actual text or media), 2) Padding (transparent area around content), 3) Border (frame surrounding padding), and 4) Margin (clearance outside border)."
        },
        {
            "id": "gen_c3",
            "question": "What is the difference between an ID and a Class selector in CSS?",
            "hint": "Explain uniqueness (# vs .) and specificity rules.",
            "star_guide": "S: Refactoring CSS for reusability. T: Organize selectors cleanly. A: Used classes for reusable design components and reserved IDs for unique page sections. R: Eliminated CSS specificity conflicts.",
            "sample_answer": "An ID selector (prefixed with #) is unique and should only be used on a single element per page, carrying higher specificity. A Class selector (prefixed with .) can be applied to multiple elements, making it ideal for reusable component styling."
        }
    ],
    "JavaScript": [
        {
            "id": "gen_js1",
            "question": "What is JavaScript?",
            "hint": "Client-side scripting language, interactivity, running in web browsers and Node.js.",
            "star_guide": "S: Building a dynamic web page. T: Add user interactivity. A: Wrote JavaScript to handle click events, form validation, and DOM updates. R: Responsive and engaging user experience.",
            "sample_answer": "JavaScript is a lightweight, dynamic, interpreted programming language widely used to make web pages interactive and dynamic. It runs directly in the browser to handle user events, modify HTML content, validate forms, and communicate with backend servers via APIs."
        },
        {
            "id": "gen_js2",
            "question": "What is the difference between var, let, and const in JavaScript?",
            "hint": "Function scope vs block scope, and reassignability.",
            "star_guide": "S: Writing modern clean JavaScript. T: Prevent variable hoisting and scope leak bugs. A: Used const for constants and let for mutable variables, avoiding var. R: Bug-free scoped execution.",
            "sample_answer": "'var' is function-scoped and can be re-declared and hoisted. 'let' is block-scoped and allows reassignment but not re-declaration within the same scope. 'const' is block-scoped and cannot be reassigned after its initial declaration."
        },
        {
            "id": "gen_js3",
            "question": "What is the difference between == and === in JavaScript?",
            "hint": "Loose equality with type coercion vs strict equality without type coercion.",
            "star_guide": "S: Comparing user inputs in form validation. T: Eliminate type coercion errors. A: Standardized all comparisons to strict equality ===. R: Reliable boolean logic throughout the codebase.",
            "sample_answer": "The == operator (loose equality) compares two values for equality after performing automatic type conversion (type coercion). The === operator (strict equality) compares both value and data type without any type conversion."
        }
    ],
    "Java": [
        {
            "id": "gen_j1",
            "question": "What is Java?",
            "hint": "High-level, class-based, object-oriented, 'Write Once, Run Anywhere' (WORA), JVM.",
            "star_guide": "S: Developing enterprise backend services. T: Leverage platform independence. A: Built services in Java compiled to bytecode running on JVM. R: Reliable cross-platform enterprise software.",
            "sample_answer": "Java is a high-level, class-based, object-oriented programming language designed for portability. It follows the 'Write Once, Run Anywhere' (WORA) principle, meaning compiled Java bytecode can run on any platform equipped with a Java Virtual Machine (JVM)."
        },
        {
            "id": "gen_j2",
            "question": "What are the four main principles of Object-Oriented Programming (OOP) in Java?",
            "hint": "Encapsulation, Inheritance, Polymorphism, Abstraction.",
            "star_guide": "S: Designing domain classes. T: Structure clean, reusable code. A: Implemented encapsulation with private fields, inheritance for shared logic, and polymorphism for service interfaces. R: Modular, maintainable codebase.",
            "sample_answer": "The four main principles of OOP in Java are: 1) Encapsulation (bundling data and methods together and restricting direct field access), 2) Inheritance (allowing a class to acquire properties of another class), 3) Polymorphism (allowing one interface or method to take many forms), and 4) Abstraction (hiding complex implementation details and showing only essential features)."
        },
        {
            "id": "gen_j3",
            "question": "What is the difference between JDK, JRE, and JVM in Java?",
            "hint": "JDK = Development Kit, JRE = Runtime Environment, JVM = Virtual Machine.",
            "star_guide": "S: Setting up CI/CD environments. T: Configure proper Java dependencies. A: Installed JDK on dev machines and JRE/JVM on deployment servers. R: Smooth compilation and runtime.",
            "sample_answer": "JVM (Java Virtual Machine) executes Java bytecode. JRE (Java Runtime Environment) bundles the JVM along with standard libraries required to run Java applications. JDK (Java Development Kit) contains the complete development environment including JRE, compiler (javac), and debugger."
        }
    ],
    "Python": [
        {
            "id": "gen_p1",
            "question": "What is Python?",
            "hint": "High-level, interpreted, dynamically typed, clean readable syntax, and general-purpose nature.",
            "star_guide": "S: Selecting language for backend and automation. T: Rapid prototyping and clean code. A: Chose Python for its readable syntax and rich ecosystem. R: Delivered reliable APIs quickly.",
            "sample_answer": "Python is a high-level, interpreted, general-purpose programming language known for its clear, readable syntax and versatility. It supports multiple programming paradigms (procedural, object-oriented, and functional) and is widely used in web development, data science, AI, and automation."
        },
        {
            "id": "gen_p2",
            "question": "What is the difference between a List and a Tuple in Python?",
            "hint": "Mutability (can modify vs cannot modify) and syntax ([] vs ()).",
            "star_guide": "S: Designing data structures. T: Choose appropriate collection types. A: Used immutable tuples for fixed coordinates/keys and lists for dynamic collections. R: Memory efficiency and accidental modification prevention.",
            "sample_answer": "A List in Python is mutable (its elements can be modified, added, or removed) and defined using square brackets []. A Tuple is immutable (its elements cannot be changed once created) and defined using parentheses ()."
        },
        {
            "id": "gen_p3",
            "question": "What is a function in Python and how do you define one?",
            "hint": "def keyword, function name, parameters, colon, indentation, and return statement.",
            "star_guide": "S: Refactoring repetitive code. T: Modularize logic into functions. A: Defined modular functions with def, docstrings, and return statements. R: Highly readable and reusable codebase.",
            "sample_answer": "A function in Python is a reusable block of organized code designed to perform a single, related action. It is defined using the 'def' keyword, followed by the function name, parentheses for parameters, a colon, and an indented code block, optionally returning a value with 'return'."
        }
    ],
    "Technical": [
        {
            "id": "gen_t1",
            "question": "What is an API?",
            "hint": "Application Programming Interface, client-server communication, JSON data exchange.",
            "star_guide": "S: Connecting frontend with backend. T: Enable data exchange. A: Built RESTful APIs returning structured JSON data. R: Seamless communication between client and server.",
            "sample_answer": "An API (Application Programming Interface) is a set of rules and protocols that allows different software applications to communicate with each other. In web development, web APIs allow the frontend to request and receive data (such as JSON) from a backend server."
        },
        {
            "id": "gen_t2",
            "question": "What is the difference between Frontend and Backend development?",
            "hint": "Client-side (UI, HTML, CSS, JS) vs server-side (databases, server logic, APIs).",
            "star_guide": "S: Designing full-stack architecture. T: Differentiate responsibilities. A: Assigned visual UI to frontend and databases and business logic to backend. R: Clear architecture and separation of concerns.",
            "sample_answer": "Frontend development focuses on the client-side—the visual user interface, layout, and user interactions built with HTML, CSS, and JavaScript. Backend development deals with the server-side—managing business logic, authentication, APIs, and databases behind the scenes."
        },
        {
            "id": "gen_t3",
            "question": "What is a Database and what is the difference between SQL and NoSQL?",
            "hint": "Structured relational tables (SQL) vs flexible documents or key-values (NoSQL).",
            "star_guide": "S: Selecting persistence layer. T: Model application data. A: Evaluated relational SQL (PostgreSQL) vs document NoSQL (MongoDB). R: Selected optimal database for schema requirements.",
            "sample_answer": "A database is an organized system for storing and managing data. SQL databases (relational) store data in structured tables with fixed schemas and relationships (like MySQL or PostgreSQL). NoSQL databases (non-relational) store data in flexible documents, key-values, or graphs (like MongoDB or Redis)."
        }
    ],
    "Behavioral": [
        {
            "id": "gen_b1",
            "question": "Tell me about yourself and your journey in software development.",
            "hint": "Summarize background, key programming skills learned, projects built, and current career focus.",
            "star_guide": "S: Introducing candidate profile. T: Deliver concise professional summary. A: Highlighted technical passion, core languages mastered, and project achievements. R: Strong, authentic interview opening.",
            "sample_answer": "Introduce your educational background, share what inspired you to learn programming, mention the key languages and tools you enjoy using (e.g. HTML, CSS, JavaScript, Python, or Java), and express your enthusiasm for building practical software applications."
        },
        {
            "id": "gen_b2",
            "question": "Describe a challenge you faced while working on a project and how you resolved it.",
            "hint": "Use Situation, Task, Action, Result (STAR) framework.",
            "star_guide": "S: Encountered unexpected technical roadblock. T: Diagnose and fix issue under deadline. A: Researched documentation, tested isolated components, and implemented fix. R: Shipped working feature on time.",
            "sample_answer": "Describe the specific problem or bug you encountered (Situation/Task), the debugging steps and research you conducted to understand the root cause (Action), and the successful solution you implemented along with what you learned (Result)."
        }
    ],
    "System Design": [
        {
            "id": "gen_s1",
            "question": "What is Client-Server Architecture?",
            "hint": "Client requests service, Server processes and provides response.",
            "star_guide": "S: Explaining network architecture. T: Outline system components. A: Clarified how browser clients communicate over HTTP with backend web servers. R: Clear system comprehension.",
            "sample_answer": "Client-Server architecture is a distributed framework where the client (such as a web browser or mobile app) sends requests over a network, and the server processes the request and returns the requested data or resource."
        },
        {
            "id": "gen_s2",
            "question": "What is Web Caching and why is it used?",
            "hint": "Temporary storage of frequently requested data to reduce server load and latency.",
            "star_guide": "S: Optimizing page load times. T: Reduce origin server bottlenecks. A: Configured browser and CDN caching for static assets. R: Decreased page load latency significantly.",
            "sample_answer": "Web caching is the process of storing copies of web files or database query results in temporary storage (such as browser cache, CDN, or Redis) so that future requests can be served much faster without querying the origin server each time."
        }
    ]
}


def extract_text_from_file_stream(file_stream, filename):
    """Parses .pdf, .docx, .txt, .md files into raw string text."""
    ext = os.path.splitext(filename)[1].lower()
    text = ""
    try:
        if ext == '.pdf':
            if pypdf:
                reader = pypdf.PdfReader(file_stream)
                for page in reader.pages:
                    txt = page.extract_text()
                    if txt:
                        text += txt + "\n"
            else:
                text = file_stream.read().decode('utf-8', errors='ignore')
        elif ext == '.docx':
            if docx:
                doc = docx.Document(file_stream)
                for p in doc.paragraphs:
                    if p.text:
                        text += p.text + "\n"
            else:
                text = file_stream.read().decode('utf-8', errors='ignore')
        else:
            text = file_stream.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"[File Parse Warning] {filename}: {e}")
        try:
            file_stream.seek(0)
            text = file_stream.read().decode('utf-8', errors='ignore')
        except Exception:
            text = ""
    return text.strip()


# ============================================================================
# PAGE ROUTES
# ============================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/interview')
def interview_page():
    return render_template('interview.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/practice')
def practice_page():
    return render_template('practice.html')

@app.route('/resume-analyzer')
def resume_analyzer_page():
    return render_template('resume_analyzer.html')


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.json or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    target_role = data.get('target_role', 'Software Engineer')

    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required."}), 400

    existing_user = db_manager.get_user_by_email(email)
    if existing_user:
        return jsonify({"success": False, "error": "User with this email already exists."}), 400

    new_user = {
        "email": email,
        "password": password,
        "full_name": full_name or email.split('@')[0].capitalize(),
        "target_role": target_role,
        "target_level": "Mid-Senior",
        "created_at": int(time.time())
    }
    created = db_manager.create_user(new_user)
    session['user_id'] = created['id']
    session['user_name'] = created['full_name']
    session['user_email'] = created['email']

    return jsonify({"success": True, "user": created})


@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.json or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    user = db_manager.get_user_by_email(email)
    if not user or user.get('password') != password:
        return jsonify({"success": False, "error": "Invalid email or password."}), 401

    session['user_id'] = user['id']
    session['user_name'] = user.get('full_name', 'User')
    session['user_email'] = user['email']

    return jsonify({"success": True, "user": user})


@app.route('/api/auth/current-user', methods=['GET'])
def api_current_user():
    user_id = session.get('user_id')
    email = session.get('user_email')
    
    if not user_id and not email:
        return jsonify({"success": True, "authenticated": False, "user": None})
        
    user = db_manager.get_user_by_email(email) if email else None
    if not user:
        user = {
            "id": user_id or "user_demo",
            "full_name": session.get('user_name', 'Alex Mercer'),
            "email": email or "demo@interview.ai",
            "target_role": "Full Stack Engineer",
            "target_level": "Senior"
        }
    return jsonify({"success": True, "authenticated": True, "user": user})


@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully."})



@app.route('/api/interview/start', methods=['POST'])
def api_interview_start():
    data = request.json or {}
    role = data.get('role', 'Full Stack Developer')
    category = data.get('category', 'Technical')
    difficulty = data.get('difficulty', 'Senior')
    questions_count = int(data.get('questions_count', 3))

    pool = AI_QUESTION_POOL.get(category, AI_QUESTION_POOL.get('Technical', []))
    if not pool:
        pool = AI_QUESTION_POOL['Technical']

    selected_questions = random.sample(pool, min(questions_count, len(pool)))

    # If count requested is larger than sample, duplicate or customize
    while len(selected_questions) < questions_count:
        q_copy = dict(random.choice(pool))
        q_copy['id'] = f"gen_{random.randint(100, 999)}"
        q_copy['question'] = f"Custom {category} ({role}): {q_copy['question']}"
        selected_questions.append(q_copy)

    session_id = f"session_{int(time.time())}"
    return jsonify({
        "success": True,
        "session_id": session_id,
        "role": role,
        "category": category,
        "difficulty": difficulty,
        "questions": selected_questions
    })


@app.route('/api/interview/evaluate', methods=['POST'])
def api_interview_evaluate():
    data = request.json or {}
    question_text = data.get('question', '')
    user_answer = data.get('user_answer', '').strip()
    category = data.get('category', 'Technical')
    difficulty = data.get('difficulty', 'Junior')

    word_count = len(user_answer.split())
    answer_lower = user_answer.lower()
    q_lower = question_text.lower()

    # Negative signals / explicit admissions / non-answers
    explicit_wrong_phrases = [
        "don't know", "dont know", "no idea", "wrong answer", "idk", "not sure",
        "nothing", "skip", "i do not know", "have no clue", "dunno", "no clue", "can't answer"
    ]
    is_explicitly_wrong = any(phrase in answer_lower for phrase in explicit_wrong_phrases)

    # Domain specific keywords for basic questions
    topic_keywords = {
        "html": ["markup", "hypertext", "hyper text", "structure", "tag", "element", "web page", "webpage", "document", "skeleton", "doctype"],
        "css": ["style", "styling", "cascading", "design", "color", "layout", "presentation", "appearance", "font", "box model", "flexbox"],
        "javascript": ["script", "interactive", "dynamic", "browser", "client", "programming", "event", "dom", "variable", "function", "node"],
        "python": ["python", "programming", "interpreted", "language", "code", "syntax", "high-level", "script", "list", "tuple", "def"],
        "java": ["java", "object-oriented", "oop", "class", "jvm", "bytecode", "programming", "wora", "jdk", "jre", "encapsulation", "equals"],
        "api": ["interface", "application programming", "communicate", "endpoint", "request", "response", "data", "protocol", "json", "rest"],
        "database": ["database", "store", "table", "sql", "nosql", "relational", "schema", "record", "query", "mongodb", "data"]
    }

    # Detect which topic is being tested
    matched_topic = None
    for topic_key in topic_keywords:
        if topic_key in q_lower:
            matched_topic = topic_key
            break

    is_conceptually_wrong = False
    matching_keywords = []
    if matched_topic:
        req_words = topic_keywords[matched_topic]
        matching_keywords = [w for w in req_words if w in answer_lower]
        # If user answer has 0 relevant concept words and is brief or unrelated
        if len(matching_keywords) == 0 and word_count < 14:
            is_conceptually_wrong = True

    # Obvious contradictions
    if "html is a programming language" in answer_lower or "css is a backend" in answer_lower or "css is backend" in answer_lower or "java is javascript" in answer_lower:
        is_conceptually_wrong = True

    # If answer is wrong, too brief (< 4 words), or explicitly incorrect -> STRICT 0 OUT OF 10
    if is_explicitly_wrong or is_conceptually_wrong or word_count < 4:
        score = 0.0  # STRICT 0 OUT OF 10 FOR WRONG ANSWERS!
        is_wrong = True
        status = "Your answer is wrong (0 / 10)"
        error_rationale = f"Your response is incorrect or lacks the core concepts required for this basic question. No partial credit is awarded (0 / 10)."
        correction = f"Accurate Concept: A complete and accurate answer must define the core principles of {category}."
        strengths = ["Response was processed."]
        gaps = [
            "Your answer is wrong (0 / 10 points awarded).",
            "Missing accurate core technical definition.",
            "Review the model answer below to master this foundational concept."
        ]
        sample_ideal = f"Ideal Answer Blueprint: Provide a concise definition, explain what {category} does, and give a clear practical example."
    elif len(matching_keywords) >= 2 or word_count >= 16:
        score = round(random.uniform(8.5, 9.8), 1)
        is_wrong = False
        status = "Excellent"
        error_rationale = ""
        correction = "Your answer is accurate and articulates the essential concepts well."
        strengths = [
            f"Correctly identified key principles of {category}.",
            "Clear technical terminology.",
            "Accurate and well-articulated response."
        ]
        gaps = ["To achieve a perfect 10/10, consider adding a brief code syntax example or production use-case."]
        sample_ideal = "Your answer covers all critical points effectively."
    else:
        score = round(random.uniform(6.5, 7.5), 1)
        is_wrong = False
        status = "Good Effort"
        error_rationale = ""
        correction = "Your answer captures basic concepts but could be more complete and precise."
        strengths = ["Identified basic terms correctly.", "Good structure."]
        gaps = ["Elaborate slightly more on the purpose and core mechanisms."]
        sample_ideal = "Expand your definition by mentioning the underlying mechanisms."

    follow_up = f"Based on your response regarding '{category}', can you give a simple real-world example of how you have used it in a project?"

    return jsonify({
        "success": True,
        "score": score,
        "is_wrong": is_wrong,
        "status": status,
        "error_rationale": error_rationale,
        "correction": correction,
        "strengths": strengths,
        "gaps": gaps,
        "sample_ideal": sample_ideal,
        "follow_up": follow_up
    })


@app.route('/api/interview/finish', methods=['POST'])
def api_interview_finish():
    data = request.json or {}
    user_id = session.get('user_id', 'user_demo')
    
    interview_record = {
        "user_id": user_id,
        "role": data.get('role', 'Software Engineer'),
        "topic": data.get('category', 'General Technical'),
        "difficulty": data.get('difficulty', 'Mid-Senior'),
        "date": time.strftime("%Y-%m-%d"),
        "score": float(data.get('average_score', 8.5)),
        "duration": f"{data.get('duration_seconds', 300) // 60} mins",
        "questions_count": data.get('questions_count', 3),
        "feedback": data.get('summary_feedback', 'Strong performance overall with sound technical knowledge.')
    }
    
    saved = db_manager.save_interview(interview_record)
    return jsonify({"success": True, "record": saved})


@app.route('/api/practice/questions', methods=['GET'])
def api_practice_questions():
    category = request.args.get('category', 'All')
    domain = request.args.get('domain', 'All')
    questions = db_manager.get_questions(category=category, domain=domain)
    return jsonify({"success": True, "questions": questions})


@app.route('/api/resume/analyze', methods=['POST'])
def api_resume_analyze():
    resume_text = ""
    job_description = ""

    # Check if multipart form upload (file + text fields)
    if request.files and 'resume_file' in request.files:
        file_obj = request.files['resume_file']
        filename = file_obj.filename or "resume.txt"
        resume_text = extract_text_from_file_stream(file_obj.stream, filename)
        job_description = request.form.get('job_description', '').strip()
    else:
        data = request.json or {}
        resume_text = data.get('resume_text', '').strip()
        job_description = data.get('job_description', '').strip()

    if not resume_text:
        return jsonify({"success": False, "error": "Please paste resume text or upload a resume file (.pdf, .docx, .txt)."}), 400

    if not job_description:
        job_description = "Software Engineer requiring Python, React, JavaScript, HTML, CSS, Java, REST APIs, SQL, Docker, AWS, System Architecture, and Agile practices."

    resume_words = set(resume_text.lower().split())
    jd_words = set(job_description.lower().split())

    keywords = [
        "python", "javascript", "react", "html", "css", "java", "aws", "docker", 
        "kubernetes", "microservices", "sql", "mongodb", "rest api", "graphql", 
        "ci/cd", "system design", "redis", "node.js", "git", "agile"
    ]

    matched_kw = [kw for kw in keywords if kw in resume_words and kw in jd_words]
    missing_kw = [kw for kw in keywords if kw in jd_words and kw not in resume_words]

    if not matched_kw:
        matched_kw = ["problem solving", "software engineering", "team collaboration"]

    if not missing_kw:
        missing_kw = ["system design", "performance optimization", "cloud deployment"]

    match_score = min(98, max(55, int(len(matched_kw) / max(1, len(matched_kw) + len(missing_kw)) * 100) + random.randint(10, 20)))

    # Feedback points
    feedback_points = [
        f"Strong technical alignment detected with key terms: {', '.join(matched_kw[:5])}.",
        f"Missing critical target stack keywords: {', '.join(missing_kw[:5])}.",
        "Formatting Check: Ensure work experience bullet points begin with strong action verbs (e.g., 'Engineered', 'Optimized', 'Architected').",
        "Metrics & Quantifiable Impact: Add specific percentage or dollar impact metrics to demonstrate concrete business outcomes."
    ]

    # Corrections
    corrections = [
        f"Add '{missing_kw[0]}' and '{missing_kw[1] if len(missing_kw) > 1 else 'System Design'}' to your Technical Skills section.",
        "Replace passive bullet phrasing (e.g., 'Responsible for APIs') with active phrasing (e.g., 'Architected high-throughput REST APIs handling 100k daily requests').",
        "Include a dedicated 'Core Competencies' section near the top of your resume for ATS parsers."
    ]

    # Formatted Resume Output
    formatted_resume = f"""# ALEX MERCER
**Senior Software Engineer | Full-Stack Architect**
Email: alex.mercer@example.com | Phone: +1 (555) 019-2834 | LinkedIn: linkedin.com/in/alexmercer | GitHub: github.com/alexmercer

---

## PROFESSIONAL SUMMARY
Results-driven Senior Software Engineer with 5+ years of experience engineering high-performance web applications, scalable backend microservices, and cloud architectures. Expert in {', '.join(matched_kw[:4])}. Demonstrated track record of optimizing latency, driving zero-downtime deployments, and elevating developer velocity.

---

## TECHNICAL SKILLS
- **Programming Languages**: {', '.join([k.capitalize() for k in matched_kw if k in ['python', 'javascript', 'java', 'sql', 'html', 'css']] or ['Python', 'JavaScript', 'Java', 'HTML', 'CSS'])}
- **Frameworks & Frontend**: React, Node.js, Express, Flask, HTML5, CSS3/Grid/Flexbox
- **Databases & Caching**: PostgreSQL, MongoDB, Redis, MySQL
- **Cloud & DevOps**: AWS (EC2, S3, Lambda), Docker, Kubernetes, CI/CD Pipelines, Git
- **Target Competencies**: {', '.join([k.capitalize() for k in missing_kw[:4]])}

---

## WORK EXPERIENCE

### **Senior Full-Stack Engineer** | TechSphere Solutions
*Jan 2023 – Present*
- Architected and deployed microservices architecture handling 2M+ active daily API calls with 99.99% uptime.
- Integrated automated CI/CD pipeline using Docker and GitHub Actions, reducing deployment cycle time by 45%.
- Refactored legacy frontend codebases using React, HTML5, and CSS variables, improving Web Vitals (LCP) from 3.2s to 1.1s.
- Conducted technical code reviews and mentored 6 junior engineers on clean code and design patterns.

### **Software Engineer** | DataPulse Systems
*Jun 2021 – Dec 2022*
- Engineered Python and Java backend web APIs to process real-time telemetry datasets.
- Optimized SQL database indexing and Redis caching layer, accelerating average query response times by 65%.
- Implemented JWT stateless auth with HttpOnly cookie handling for secure multi-tenant sessions.

---

## EDUCATION & CERTIFICATIONS
- **B.S. in Computer Science** – State University of Technology (2017 – 2021)
- **AWS Certified Solutions Architect – Associate**
"""

    tailored_questions = [
        f"The job description emphasizes '{missing_kw[0]}'. How have you applied this in past production systems?",
        f"Your resume highlights experience with '{matched_kw[0]}'. Can you walk me through your most complex architectural trade-off involving it?",
        "How do you measure and optimize API latency and database bottlenecks in high-concurrency environments?"
    ]

    return jsonify({
        "success": True,
        "match_score": match_score,
        "matched_keywords": matched_kw,
        "missing_keywords": missing_kw,
        "feedback_points": feedback_points,
        "corrections": corrections,
        "formatted_resume": formatted_resume.strip(),
        "tailored_questions": tailored_questions,
        "summary": f"Your resume demonstrates a strong baseline alignment ({match_score}% match). Incorporating the corrections and formatted resume structure below will maximize ATS parsing and callback rates."
    })


@app.route('/api/dashboard/history/clear', methods=['POST', 'DELETE'])
def api_dashboard_history_clear():
    user_id = session.get('user_id', 'user_demo')
    db_manager.clear_user_interviews(user_id)
    return jsonify({"success": True, "message": "Interview history cleared. You can start fresh!"})


@app.route('/api/dashboard/history/<interview_id>', methods=['DELETE'])
def api_dashboard_history_delete(interview_id):
    user_id = session.get('user_id', 'user_demo')
    db_manager.delete_interview(interview_id, user_id=user_id)
    return jsonify({"success": True, "message": "Session deleted successfully."})


@app.route('/api/dashboard/stats', methods=['GET'])
def api_dashboard_stats():
    user_id = session.get('user_id', 'user_demo')
    interviews = db_manager.get_user_interviews(user_id)
    
    if not interviews:
        avg_score = 0.0
        completed_count = 0
        total_practice_hours = 0.0
        prep_streak_days = 0
        skill_matrix = {
            "HTML & CSS": 0,
            "JavaScript / Python": 0,
            "Java & OOP": 0,
            "System Design": 0,
            "Behavioral (STAR)": 0
        }
    else:
        scores = [i.get('score', 0.0) for i in interviews]
        avg_score = round(sum(scores) / max(1, len(scores)), 1)
        completed_count = len(interviews)
        total_practice_hours = round(len(interviews) * 0.4, 1)
        prep_streak_days = min(7, len(interviews) + 1)
        skill_matrix = {
            "HTML & CSS": 85,
            "JavaScript / Python": 88,
            "Java & OOP": 80,
            "System Design": 75,
            "Behavioral (STAR)": 90
        }

    data = {
        "average_score": avg_score,
        "completed_count": completed_count,
        "total_practice_hours": total_practice_hours,
        "prep_streak_days": prep_streak_days,
        "skill_matrix": skill_matrix,
        "history": interviews
    }
    return jsonify({"success": True, "stats": data})


if __name__ == '__main__':
    print("\n========================================================")
    print(" Aptivox AI backend starting...")
    print(" Access UI at: http://127.0.0.1:5000")
    print("========================================================\n")
    app.run(debug=True, port=5000)

