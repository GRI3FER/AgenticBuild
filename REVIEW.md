# Code Review: 15-112 Quiz Application

**Date:** March 28, 2026  
**Files Reviewed:** quiz.py, user_manager.py, questions.json  
**Specification Reference:** SPEC.md

---

## ACCEPTANCE CRITERIA VERIFICATION

1. [PASS] **App must initialize and ask how many questions**
   - File: [quiz.py](quiz.py#L48), Method: `get_num_questions()`
   - Correctly prompts user with "Hi, how many questions do you want to do today?" and validates numeric input

2. [PASS] **App must ask only that many questions**
   - File: [quiz.py](quiz.py#L104), Method: `get_filtered_questions()`
   - File: [quiz.py](quiz.py#L155), Method: `run_quiz()`
   - Filters questions correctly and iterates exactly `num_questions` times through the quiz loop

3. [FAIL] **App must not crash if the answer is empty or not an expected answer**
   - File: [quiz.py](quiz.py#L133-L138), Method: `ask_short_answer()`
   - **Issue:** Recursive call for empty answers can cause `RecursionError` if user repeatedly enters empty input
   - **Severity:** HIGH - Violates acceptance criteria by allowing crash
   - **Fix:** Replace recursion with a `while` loop instead of recursive call
   - **Note:** Multiple choice (line 113) and true/false (line 123) handle this correctly with loops

4. [PASS] **App must only ask questions from the question bank**
   - File: [quiz.py](quiz.py#L101-L107), Method: `get_filtered_questions()`
   - Correctly loads questions from questions.json and filters by difficulty
   - File: [questions.json](questions.json) - 53 total questions properly formatted

5. [FAIL] **App must update questions based on student input**
   - **Missing Feature:** No feedback system implemented
   - **Specification Requirement:** "Users should somehow be able to provide feedback on whether they like a question or not, and this should inform what questions they get next"
   - **Current State:** Application asks questions but provides no way for students to provide feedback, and no logic to adjust future questions based on feedback
   - **Severity:** HIGH - Core feature from acceptance criteria not implemented

6. [PASS] **App must accurately calculate scores and consistently print them**
   - File: [quiz.py](quiz.py#L145-L167), Method: `run_quiz()`
   - Scoring calculation verified:
     - Easy: 10 pts × multiplier ✓
     - Medium: 20 pts × multiplier ✓
     - Hard: 30 pts × multiplier ✓
   - Streak multiplier formula correct: `1.1 ** (streak - 1)` [quiz.py:162]
   - Score printed after each question [quiz.py:167]
   - Final score displayed [quiz.py:170]

---

## ERROR HANDLING VERIFICATION

1. [PASS] **Invalid number input: "not a number please input a number"**
   - File: [quiz.py](quiz.py#L52)
   - Exact error message matches specification

2. [PASS] **Missing question bank: "there is no question bank"**
   - File: [quiz.py](quiz.py#L89)
   - Exact error message matches specification

3. [PASS] **Too many questions requested: "please choose a number less than [X]"**
   - File: [quiz.py](quiz.py#L94-L95)
   - Dynamic message correctly inserts available question count

---

## CORE FEATURES VERIFICATION

1. [PASS] **Local login system with registration**
   - File: [user_manager.py](user_manager.py#L33-L63), Methods: `register()` and `login()`
   - File: [quiz.py](quiz.py#L28-L46), Method: `authenticate_user()`
   - Both new user registration and existing user login implemented

2. [PASS] **Password security - not easily discoverable**
   - File: [user_manager.py](user_manager.py#L22-L24), Method: `hash_password()`
   - Uses SHA-256 hashing (industry-standard cryptographic hash)
   - Passwords are never stored in plaintext

3. [PASS] **Score history file - non-human-readable and secure**
   - File: [user_manager.py](user_manager.py#L65-L104), Methods: `save_score()` and `load_score_history()`
   - Uses Base64 encoding for obfuscation (not cryptographic encryption)
   - File path: `score_history.bin`
   - User data file: `users_data.bin` is also Base64-encoded
   - **Note:** See Security Concerns section below

4. [PASS] **Questions in human-readable JSON format**
   - File: [questions.json](questions.json)
   - Proper JSON formatting with clear structure
   - Easy to modify for other subjects/topics
   - 53 total questions across 3 difficulty levels

5. [PASS] **Project structure: At least 2 .py files and 1 .json file**
   - Python files: `quiz.py`, `user_manager.py` ✓
   - JSON file: `questions.json` ✓

---

## BUGS & LOGIC ERRORS

1. [FAIL] **Stack overflow risk in short answer input validation**
   - File: [quiz.py](quiz.py#L133-L138)
   - **Issue:** Recursive function call without depth limit can cause `RecursionError`
   ```python
   def ask_short_answer(self, question_data):
       # ... code ...
       if not user_input:
           print("Answer cannot be empty. Please try again.")
           return self.ask_short_answer(question_data)  # ← RECURSION
   ```
   - **Fix:** Replace with a `while True:` loop:
   ```python
   while True:
       user_input = input("Your answer: ").strip().lower()
       if user_input:
           return user_input
       print("Answer cannot be empty. Please try again.")
   ```
   - **Impact:** User repeatedly pressing Enter without input causes crash

---

## CODE QUALITY ISSUES

1. [WARN] **Bare except clauses catching all exceptions**
   - File: [quiz.py](quiz.py#L29), Method: `load_questions()`
   - File: [quiz.py](quiz.py#L47), Method: `load_questions()` (second catch)
   - File: [user_manager.py](user_manager.py#L47), `load_users()`
   - File: [user_manager.py](user_manager.py#L96), `load_score_history()`
   - **Issue:** Bare `except:` silently catches all exceptions including `KeyboardInterrupt` and `SystemExit`
   - **Recommendation:** Catch specific exceptions (e.g., `except json.JSONDecodeError:` or `except (IOError, json.JSONDecodeError):`)
   - **Example of issue:** If JSON file is corrupted, function returns `None` silently instead of informing user

2. [WARN] **Magic number: Streak multiplier constant**
   - File: [quiz.py](quiz.py#L162)
   - Hardcoded `1.1` multiplier scattered in calculation
   - **Fix:** Add at module level:
   ```python
   STREAK_MULTIPLIER = 1.1
   ```
   - Then use: `self.multiplier = STREAK_MULTIPLIER ** (self.streak - 1)`

3. [WARN] **Incomplete error handling in quiz loop**
   - File: [quiz.py](quiz.py#L189-L204)
   - Generic `except Exception` clause in `run()` method
   - **Issue:** Broad exception handling masks programming errors
   - **Recommendation:** Catch specific exceptions or let errors propagate during development

4. [WARN] **No input validation for difficulty level edge case**
   - File: [quiz.py](quiz.py#L70)
   - `get_difficulty()` method loops on invalid input but doesn't validate against actual question data first
   - Minor issue as it catches invalid difficulty before querying questions

5. [INFO] **No type hints in codebase**
   - File: [quiz.py](quiz.py), [user_manager.py](user_manager.py)
   - While not a bug, type hints would improve code clarity and enable static type checking
   - Recommendation: Add type hints to method signatures (Python 3.5+ feature)

---

## SECURITY CONCERNS

1. [WARN] **Base64 is encoding, not encryption**
   - File: [user_manager.py](user_manager.py#L47), Line saving users to file
   - File: [user_manager.py](user_manager.py#L70), Line saving scores to file
   - **Issue:** Base64 can be trivially decoded by anyone with file access
   - **Current State:** Base64-encoded, not encrypted
   - **Status:** Acceptable per spec which states "relatively secure" and acknowledges usernames may be discoverable
   - **Mitigation:** Spec acknowledges this limitation; usernames are visible, passwords and scores cannot be easily read without decoding
   - **Severity:** LOW (spec requirements met, but note architecture limitation)

2. [PASS] **Password storage is secure**
   - File: [user_manager.py](user_manager.py#L22-L24)
   - SHA-256 hashing prevents password recovery even if database is compromised
   - No salt added - **minor security note:** Using salt would be better, but SHA-256 without salt is still strong for small-scale applications

3. [PASS] **File permissions**
   - No explicit file permission issues identified
   - `.bin` files (users_data.bin, score_history.bin) are created with default permissions
   - On Unix-like systems: readable by user, group, others by default - could be restricted further via `os.chmod()`

---

## MISSING FEATURES

1. [FAIL] **Question feedback system not implemented**
   - Specification requirement: "Users should somehow be able to provide feedback on whether they like a question or not, and this should inform what questions they get next"
   - **Current State:** No UI to collect feedback, no logic to track preferences, no logic to adjust questions based on feedback
   - **Recommendation:** 
     - Add prompt after each question: "Did you like this question? (yes/no)"
     - Store feedback in score history with question ID
     - Modify `get_filtered_questions()` to weight questions based on user feedback
   - **Acceptance Criteria Impact:** Feature requirement from SPEC.md not implemented

---

## SUMMARY TABLE

| Category | Item | Status | Severity |
|----------|------|--------|----------|
| Acceptance Criteria #1 | Initialize and ask questions | PASS | — |
| Acceptance Criteria #2 | Ask only requested number | PASS | — |
| Acceptance Criteria #3 | No crash on empty input | FAIL | HIGH |
| Acceptance Criteria #4 | Only use question bank | PASS | — |
| Acceptance Criteria #5 | Update based on input | FAIL | HIGH |
| Acceptance Criteria #6 | Accurate scoring | PASS | — |
| Error Handling | "not a number" message | PASS | — |
| Error Handling | "no question bank" message | PASS | — |
| Error Handling | "too many questions" message | PASS | — |
| Core Features | Login system | PASS | — |
| Core Features | Password security | PASS | — |
| Core Features | Score history | PASS | — |
| Core Features | JSON questions | PASS | — |
| Core Features | File structure | PASS | — |
| Bugs | Short answer recursion | FAIL | HIGH |
| Code Quality | Bare except clauses | WARN | MEDIUM |
| Code Quality | Magic numbers | WARN | LOW |
| Code Quality | Broad exception handling | WARN | MEDIUM |
| Security | Base64 encoding | WARN | LOW |

---

## RECOMMENDATIONS (Priority Order)

### CRITICAL (Breaks Acceptance Criteria)
1. **Fix short answer recursion vulnerability** [quiz.py:133-138]
   - Replace recursive call with while loop to prevent stack overflow
   
2. **Implement question feedback system**
   - Add feedback prompts after questions
   - Store feedback in user's score history
   - Adjust future question selection based on feedback

### HIGH PRIORITY (Code Quality)
3. **Replace bare except clauses with specific exception handling**
   - Replace all bare `except:` with `except (IOError, json.JSONDecodeError):`
   - Improves debuggability and prevents silencing critical errors

### MEDIUM PRIORITY (Code Improvements)
4. **Extract magic number to constant**
   - Define `STREAK_MULTIPLIER = 1.1` at module level
   
5. **Improve exception handling in main loop**
   - Replace broad `except Exception:` with specific exception types

### LOW PRIORITY (Enhancement)
6. **Add type hints** throughout codebase
7. **Add optional password salt** to hashing function for additional security
8. **Consider restricting file permissions** on .bin files with `os.chmod()`

---

## CONCLUSION

The application successfully implements **6 out of 8** critical requirements and **5 of 5** core features. However, it has **2 CRITICAL FAILURES**:

1. **Stack overflow vulnerability** that violates acceptance criteria #3 (no crashes on empty input)
2. **Missing feedback system** that violates acceptance criteria #5 and core feature requirement

With these issues resolved, the application would meet all specification requirements. Current state: **FUNCTIONAL BUT INCOMPLETE** - suitable for production use only after critical fixes.
