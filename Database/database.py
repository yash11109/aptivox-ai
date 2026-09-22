import os
import json
import time
import uuid

# Attempt MongoDB imports
try:
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False

# Attempt Firebase imports
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False


class DatabaseManager:
    """
    Hybrid Database Manager supporting MongoDB, Firebase Firestore, 
    and automatic fallback to local JSON storage for seamless operation.
    """
    def __init__(self, app=None):
        self.db_type = 'local'
        self.mongo_client = None
        self.mongo_db = None
        self.firestore_db = None
        self.local_file = os.path.join(os.path.dirname(__file__), 'data_store.json')
        self._init_local_store()

    def init_app(self, app):
        mongo_uri = app.config.get('MONGO_URI')
        firebase_path = app.config.get('FIREBASE_CREDENTIALS_PATH')
        
        # Try MongoDB connection
        if MONGO_AVAILABLE and mongo_uri:
            try:
                self.mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
                self.mongo_client.server_info() # Trigger exception if unreachable
                self.mongo_db = self.mongo_client[app.config.get('MONGO_DBNAME', 'ai_interview_db')]
                self.db_type = 'mongodb'
                print("[DatabaseManager] Successfully connected to MongoDB.")
                return
            except Exception as e:
                print(f"[DatabaseManager] MongoDB connection failed or not available ({e}). Trying Firebase...")

        # Try Firebase connection
        if FIREBASE_AVAILABLE and firebase_path and os.path.exists(firebase_path):
            try:
                cred = credentials.Certificate(firebase_path)
                firebase_admin.initialize_app(cred)
                self.firestore_db = firestore.client()
                self.db_type = 'firebase'
                print("[DatabaseManager] Successfully connected to Firebase Firestore.")
                return
            except Exception as e:
                print(f"[DatabaseManager] Firebase initialization failed ({e}).")

        # Fallback to local JSON engine
        self.db_type = 'local'
        print("[DatabaseManager] Operating in Zero-Config Local Data Engine mode.")

    def _init_local_store(self):
        if not os.path.exists(self.local_file):
            initial_data = {
                "users": [
                    {
                        "id": "user_demo",
                        "username": "demouser",
                        "email": "demo@interview.ai",
                        "password": "password123",
                        "full_name": "Alex Mercer",
                        "target_role": "Full Stack Engineer",
                        "target_level": "Senior"
                    }
                ],
                "interviews": [
                    {
                        "id": "int_101",
                        "user_id": "user_demo",
                        "role": "Full Stack Engineer",
                        "topic": "Python & System Design",
                        "difficulty": "Senior",
                        "date": "2026-09-01",
                        "score": 8.5,
                        "duration": "18 mins",
                        "questions_count": 5,
                        "feedback": "Strong understanding of concurrency and modular architecture. Focus on database indexing for scale."
                    },
                    {
                        "id": "int_102",
                        "user_id": "user_demo",
                        "role": "Full Stack Engineer",
                        "topic": "React & Web Performance",
                        "difficulty": "Senior",
                        "date": "2026-09-03",
                        "score": 9.0,
                        "duration": "22 mins",
                        "questions_count": 5,
                        "feedback": "Excellent explanation of virtual DOM reconciliation and state management patterns."
                    }
                ],
                "questions": [
                    {
                        "id": "q1",
                        "category": "Technical",
                        "domain": "Python",
                        "difficulty": "Medium",
                        "question": "Explain the difference between deep copy and shallow copy in Python, and how GIL affects multi-threaded applications.",
                        "star_guide": "Situation: Working on data processing. Task: Copy nested data structures safely without race conditions. Action: Use copy.deepcopy vs copy.copy and multiprocessing/asyncio for CPU-bound tasks. Result: Clean memory safety and parallel performance.",
                        "sample_answer": "A shallow copy creates a new object but inserts references to the objects found in the original. A deep copy recursively duplicates child objects. The Global Interpreter Lock (GIL) prevents true parallel execution of CPython threads for CPU-bound tasks."
                    },
                    {
                        "id": "q2",
                        "category": "Technical",
                        "domain": "Python",
                        "difficulty": "Senior",
                        "question": "How do Python decorators work under the hood? Explain function wrapping, arguments preservation with @functools.wraps, and class-based decorators.",
                        "star_guide": "S: Need reusable logging and auth middleware. T: Intercept function calls without modifying core logic. A: Implemented higher-order decorator functions taking *args, **kwargs and preserving metadata. R: Zero code duplication across 40+ endpoints.",
                        "sample_answer": "A decorator is a function that takes another function as an argument, extends its behavior without modifying it explicitly, and returns a new function. @functools.wraps preserves docstrings and function names."
                    },
                    {
                        "id": "q3",
                        "category": "Technical",
                        "domain": "HTML",
                        "difficulty": "Junior",
                        "question": "Why is Semantic HTML important for Web Accessibility (a11y) and SEO? Compare semantic elements like <header>, <article>, and <section> with plain <div> tags.",
                        "star_guide": "S: E-commerce platform accessibility audit. T: Enhance screen reader navigation and SEO rank. A: Refactored generic div layout to semantic section/article markup with proper ARIA attributes. R: Achieved 100 Lighthouse Accessibility score.",
                        "sample_answer": "Semantic HTML tags clearly describe their meaning to both browser and developer. Screen readers use semantic elements for landmarks, improving accessibility, while search engines use them to understand page structure and importance."
                    },
                    {
                        "id": "q4",
                        "category": "Technical",
                        "domain": "HTML",
                        "difficulty": "Medium",
                        "question": "What is the difference between local storage, session storage, and cookies in client-side HTML5 web storage?",
                        "star_guide": "S: Storing client session state. T: Select optimal storage mechanism for auth tokens vs user preferences. A: Used HttpOnly cookies for tokens and localStorage for dark mode preferences. R: Secured app against XSS while saving state.",
                        "sample_answer": "Cookies hold up to 4KB and are sent with every HTTP request. LocalStorage stores up to 5-10MB persistently until explicitly cleared. SessionStorage stores data only for the current tab session."
                    },
                    {
                        "id": "q5",
                        "category": "Technical",
                        "domain": "CSS",
                        "difficulty": "Medium",
                        "question": "Explain CSS Flexbox vs CSS Grid. When would you choose one over the other for responsive dashboard layouts?",
                        "star_guide": "S: Complex responsive dashboard design. T: Layout content cleanly across mobile and desktop. A: Combined CSS Grid for overall page grid and Flexbox for component internal alignment. R: Flawless responsive layout with minimal media queries.",
                        "sample_answer": "Flexbox is designed for 1-dimensional layouts (rows OR columns), perfect for navigation bars and component alignment. CSS Grid is designed for 2-dimensional layouts (rows AND columns), ideal for entire page structures."
                    },
                    {
                        "id": "q6",
                        "category": "Technical",
                        "domain": "CSS",
                        "difficulty": "Senior",
                        "question": "How does the CSS Stacking Context work with z-index, position (absolute/relative/fixed/sticky), and transform properties?",
                        "star_guide": "S: Modal popup clipped under navigation header. T: Fix z-index stacking bug. A: Identified parent opacity/transform creating a new stacking context; restructured container hierarchy. R: Modal renders correctly on top.",
                        "sample_answer": "A stacking context is created by root element, position with z-index != auto, opacity < 1, transform, or filter properties. Elements within a child stacking context cannot escape above parent's stacking order relative to siblings."
                    },
                    {
                        "id": "q7",
                        "category": "Technical",
                        "domain": "Java",
                        "difficulty": "Medium",
                        "question": "How does Java's HashMap work internally? Explain hash collision resolution (LinkedList vs Red-Black Tree in Java 8+).",
                        "star_guide": "S: High volume key-value cache performance issue. T: Explain HashMap bucket distribution. A: Calculated hash codes, tuned load factor, and leveraged Java 8 treeification when bucket length > 8. R: Maintained O(1) average lookup.",
                        "sample_answer": "HashMap relies on hashCode() and equals() to store key-value pairs in buckets. When collisions occur, keys are stored in a linked list. In Java 8+, if a bucket exceeds 8 entries, it converts to a Red-Black Tree for O(log N) lookup."
                    },
                    {
                        "id": "q8",
                        "category": "Technical",
                        "domain": "Java",
                        "difficulty": "Senior",
                        "question": "Compare synchronized blocks, ReentrantLock, and ConcurrentHashMap in Java multi-threaded application development.",
                        "star_guide": "S: Race conditions on shared state in banking API. T: Ensure thread safety under concurrent requests. A: Replaced bottleneck synchronized methods with lock-striping via ConcurrentHashMap and AtomicLong. R: Improved throughput by 4x.",
                        "sample_answer": "Synchronized blocks provide intrinsic locking per object. ReentrantLock offers advanced features like fairness, interruptible lock attempts, and tryLock(). ConcurrentHashMap uses bucket-level lock striping for high concurrency."
                    },
                    {
                        "id": "q9",
                        "category": "Behavioral",
                        "domain": "Leadership & Conflict",
                        "difficulty": "Senior",
                        "question": "Describe a situation where you had a strong technical disagreement with a teammate or lead. How did you handle it?",
                        "star_guide": "S: Architectural conflict over GraphQL vs REST. T: Reach alignment without delaying release. A: Built quick benchmark prototypes & evaluated trade-offs collaboratively. R: Selected REST with clear payload specs; delivered on time.",
                        "sample_answer": "I focus on data and objective benchmarks rather than personal opinions. I proposed building a lightweight prototype of both approaches to measure latency and developer velocity, which led to a consensus."
                    },
                    {
                        "id": "q10",
                        "category": "System Design",
                        "domain": "Backend Systems",
                        "difficulty": "Senior",
                        "question": "How would you design a rate limiter for a public API handling 100,000 requests per second?",
                        "star_guide": "S: High traffic volume API protection. T: Prevent DDoS and abuse. A: Distributed Redis sliding window counter or Token Bucket algorithm. R: 99.99% uptime with sub-millisecond throttle latency.",
                        "sample_answer": "I would use a Token Bucket or Sliding Window Log algorithm implemented using Redis with Lua scripts for atomic counter updates across distributed backend nodes."
                    }
                ]
            }
            with open(self.local_file, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=4)

    def _read_local(self):
        try:
            with open(self.local_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"users": [], "interviews": [], "questions": []}

    def _write_local(self, data):
        with open(self.local_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    # --- User Operations ---
    def get_user_by_email(self, email):
        if self.db_type == 'mongodb':
            return self.mongo_db.users.find_one({"email": email})
        elif self.db_type == 'firebase':
            docs = self.firestore_db.collection('users').where('email', '==', email).limit(1).get()
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        else:
            store = self._read_local()
            for user in store.get('users', []):
                if user.get('email') == email:
                    return user
            return None

    def create_user(self, user_data):
        user_data['id'] = user_data.get('id', str(uuid.uuid4()))
        if self.db_type == 'mongodb':
            self.mongo_db.users.insert_one(user_data)
        elif self.db_type == 'firebase':
            self.firestore_db.collection('users').document(user_data['id']).set(user_data)
        else:
            store = self._read_local()
            store['users'].append(user_data)
            self._write_local(store)
        return user_data

    # --- Interview Operations ---
    def get_user_interviews(self, user_id):
        if self.db_type == 'mongodb':
            return list(self.mongo_db.interviews.find({"user_id": user_id}, {"_id": 0}))
        elif self.db_type == 'firebase':
            docs = self.firestore_db.collection('interviews').where('user_id', '==', user_id).get()
            return [doc.to_dict() for doc in docs]
        else:
            store = self._read_local()
            return [i for i in store.get('interviews', []) if i.get('user_id') == user_id]

    def save_interview(self, interview_data):
        interview_data['id'] = interview_data.get('id', str(uuid.uuid4()))
        interview_data['timestamp'] = int(time.time())
        if self.db_type == 'mongodb':
            self.mongo_db.interviews.insert_one(interview_data)
        elif self.db_type == 'firebase':
            self.firestore_db.collection('interviews').document(interview_data['id']).set(interview_data)
        else:
            store = self._read_local()
            store['interviews'].append(interview_data)
            self._write_local(store)
        return interview_data

    def clear_user_interviews(self, user_id):
        if self.db_type == 'mongodb':
            self.mongo_db.interviews.delete_many({"user_id": user_id})
            return True
        elif self.db_type == 'firebase':
            docs = self.firestore_db.collection('interviews').where('user_id', '==', user_id).get()
            for doc in docs:
                doc.reference.delete()
            return True
        else:
            store = self._read_local()
            store['interviews'] = [i for i in store.get('interviews', []) if i.get('user_id') != user_id]
            self._write_local(store)
            return True

    def delete_interview(self, interview_id, user_id=None):
        if self.db_type == 'mongodb':
            query = {"id": interview_id}
            if user_id:
                query["user_id"] = user_id
            self.mongo_db.interviews.delete_one(query)
            return True
        elif self.db_type == 'firebase':
            self.firestore_db.collection('interviews').document(interview_id).delete()
            return True
        else:
            store = self._read_local()
            store['interviews'] = [i for i in store.get('interviews', []) if i.get('id') != interview_id]
            self._write_local(store)
            return True

    # --- Question Operations ---
    def get_questions(self, category=None, domain=None):
        if self.db_type == 'mongodb':
            query = {}
            if category and category != 'All':
                query['category'] = category
            if domain and domain != 'All':
                query['domain'] = domain
            return list(self.mongo_db.questions.find(query, {"_id": 0}))
        elif self.db_type == 'firebase':
            ref = self.firestore_db.collection('questions')
            if category and category != 'All':
                ref = ref.where('category', '==', category)
            if domain and domain != 'All':
                ref = ref.where('domain', '==', domain)
            return [doc.to_dict() for doc in ref.get()]
        else:
            store = self._read_local()
            questions = store.get('questions', [])
            filtered = []
            for q in questions:
                if category and category != 'All' and q.get('category') != category:
                    continue
                if domain and domain != 'All' and q.get('domain') != domain:
                    continue
                filtered.append(q)
            return filtered

db_manager = DatabaseManager()
