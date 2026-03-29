import json
import os
import random
from user_manager import UserManager

# Question bank file path
QUESTIONS_FILE = "questions.json"

# Points for each difficulty
DIFFICULTY_POINTS = {
    "Easy": 10,
    "Medium": 20,
    "Hard": 30
}

# Streak multiplier constant
STREAK_MULTIPLIER = 1.1

# Error message constants
ERROR_INVALID_NUMBER = "not a number please input a number"
ERROR_NO_QUESTION_BANK = "there is no question bank"
ERROR_INSUFFICIENT_QUESTIONS = "please choose a number less than {}"

# Valid question types
VALID_QUESTION_TYPES = ["multiple_choice", "true_false", "short_answer"]

class Quiz:
    def __init__(self):
        self.user_manager = UserManager()
        self.questions = self.load_questions()
        self.score = 0
        self.streak = 0
        self.multiplier = 1.0
        self.current_question_num = 0
        self.all_feedback = []  # Store feedback for all questions in current quiz
    
    def load_questions(self):
        """Load questions from JSON file with validation"""
        if not os.path.exists(QUESTIONS_FILE):
            return None
        
        try:
            with open(QUESTIONS_FILE, 'r') as f:
                data = json.load(f)
                questions = data.get("questions", [])
                
                # Validate that questions list is not empty
                if not questions:
                    print("Error: Question bank is empty")
                    return None
                
                # Validate question structure
                required_fields = ["question", "type", "answer"]
                for idx, q in enumerate(questions):
                    # Check required fields
                    if not all(field in q for field in required_fields):
                        print(f"Error: Question {idx + 1} missing required fields: {required_fields}")
                        return None
                    
                    # Check valid type
                    if q["type"] not in VALID_QUESTION_TYPES:
                        print(f"Error: Question {idx + 1} has invalid type '{q['type']}'. Must be one of: {VALID_QUESTION_TYPES}")
                        return None
                    
                    # Type-specific validation
                    if q["type"] == "multiple_choice" and "options" not in q:
                        print(f"Error: Multiple choice question {idx + 1} missing 'options' field")
                        return None
                
                return questions
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading questions file: {e}")
            return None
    
    def authenticate_user(self):
        """Handle user login or registration"""
        while True:
            print("\n" + "="*50)
            print("WELCOME TO THE 15-112 QUIZ APPLICATION")
            print("="*50)
            choice = input("\nAre you a new user? (yes/no): ").strip().lower()
            
            if choice == "yes":
                username = input("Enter a username: ").strip()
                if not username:
                    print("Username cannot be empty")
                    continue
                
                password = input("Enter a password: ").strip()
                if not password:
                    print("Password cannot be empty")
                    continue
                
                success, message = self.user_manager.register(username, password)
                print(message)
                if success:
                    self.user_manager.current_user = username
                    break
            elif choice == "no":
                username = input("Enter your username: ").strip()
                password = input("Enter your password: ").strip()
                success, message = self.user_manager.login(username, password)
                print(message)
                if success:
                    break
                else:
                    print("Login failed. Please try again.")
            else:
                print("Please enter 'yes' or 'no'")
    
    def get_num_questions(self):
        """Get the number of questions from user"""
        while True:
            user_input = input("\nHi, how many questions do you want to do today? ").strip()
            
            # Check if input is a number
            try:
                num_questions = int(user_input)
                if num_questions <= 0:
                    print("Please enter a number greater than 0")
                    continue
                return num_questions
            except ValueError:
                print(ERROR_INVALID_NUMBER)
    
    def get_difficulty(self):
        """Get difficulty level from user"""
        while True:
            difficulty = input("\nWhat difficulty do you want? (Easy/Medium/Hard): ").strip()
            if difficulty not in ["Easy", "Medium", "Hard"]:
                print("Please enter Easy, Medium, or Hard")
                continue
            return difficulty
    
    def get_filtered_questions(self, difficulty, num_questions):
        """Filter questions by difficulty, with preference weighting"""
        if self.questions is None:
            print(ERROR_NO_QUESTION_BANK)
            return None
        
        filtered = [q for q in self.questions if q["difficulty"] == difficulty]
        
        if num_questions > len(filtered):
            print(ERROR_INSUFFICIENT_QUESTIONS.format(len(filtered)))
            return None
        
        # Get user preferences (liked/disliked questions)
        user_prefs = self.user_manager.get_user_preferences()
        liked_questions = set(user_prefs.get("liked", []))
        disliked_questions = set(user_prefs.get("disliked", []))
        
        # Separate questions into preferred categories
        preferred = [q for q in filtered if q.get("question") in liked_questions]
        neutral = [q for q in filtered if q.get("question") not in liked_questions and q.get("question") not in disliked_questions]
        avoid = [q for q in filtered if q.get("question") in disliked_questions]
        
        # Select questions: prioritize preferred, then neutral, then avoid if necessary
        selected = []
        
        # Add questions from preferred list
        if len(selected) < num_questions and preferred:
            remaining_needed = num_questions - len(selected)
            sample_size = min(remaining_needed, len(preferred))
            selected.extend(random.sample(preferred, sample_size))
        
        # Add questions from neutral list
        if len(selected) < num_questions and neutral:
            remaining_needed = num_questions - len(selected)
            sample_size = min(remaining_needed, len(neutral))
            selected.extend(random.sample(neutral, sample_size))
        
        # Add questions from avoid list only if necessary
        if len(selected) < num_questions and avoid:
            remaining_needed = num_questions - len(selected)
            sample_size = min(remaining_needed, len(avoid))
            selected.extend(random.sample(avoid, sample_size))
        
        # Shuffle final selection to mix question types
        random.shuffle(selected)
        return selected
    
    def ask_multiple_choice(self, question_data):
        """Ask a multiple choice question"""
        print(f"\n{self.current_question_num}. {question_data['question']}")
        options = question_data['options']
        
        for i, option in enumerate(options, 1):
            print(f"   {i}. {option}")
        
        while True:
            user_input = input("Your answer (1-{}): ".format(len(options))).strip()
            
            try:
                choice = int(user_input)
                if 1 <= choice <= len(options):
                    answer = options[choice - 1]
                    return answer
                else:
                    print(f"Please enter a number between 1 and {len(options)}")
            except ValueError:
                print(f"not a number please input a number")
    
    def ask_true_false(self, question_data):
        """Ask a true/false question"""
        print(f"\n{self.current_question_num}. {question_data['question']}")
        
        while True:
            user_input = input("True or False? ").strip().lower()
            
            if user_input in ["true", "false", "t", "f"]:
                if user_input in ["true", "t"]:
                    return "true"
                else:
                    return "false"
            else:
                print("Please enter True, False, T, or F")
    
    def ask_short_answer(self, question_data):
        """Ask a short answer question"""
        print(f"\n{self.current_question_num}. {question_data['question']}")
        
        while True:
            user_input = input("Your answer: ").strip().lower()
            
            if user_input:
                return user_input
            else:
                print("Answer cannot be empty. Please try again.")
    
    def check_answer(self, user_answer, correct_answer):
        """Check if answer is correct"""
        user_answer = str(user_answer).lower().strip()
        correct_answer = str(correct_answer).lower().strip()
        
        return user_answer == correct_answer
    
    def calculate_score_gain(self, difficulty):
        """Calculate score gain with multiplier"""
        base_points = DIFFICULTY_POINTS[difficulty]
        return int(base_points * self.multiplier)
    
    def ask_batch_feedback(self, questions):
        """Ask user for feedback on all questions at end of quiz"""
        print("\n" + "="*50)
        print("QUESTION FEEDBACK")
        print("="*50)
        print("Now rate each question. Focus only on rating, not answering.\n")
        
        feedback_list = []
        for idx, feedback_data in enumerate(self.all_feedback, 1):
            question = questions[idx - 1]
            was_correct = feedback_data["correct"]
            
            # Show minimal info - just question number, correctness, and ask for rating
            print(f"\n--- Question {idx} ---")
            if was_correct:
                print("You got this one CORRECT ✓")
            else:
                print("You got this one INCORRECT ✗")
            
            print(f"\nQuestion: {question['question']}")
            
            # Ask only for feedback - separated clearly
            while True:
                response = input("\nDid you LIKE this question? (y/n/skip): ").strip().lower()
                if response in ["y", "n", "skip", ""]:
                    liked = None
                    if response == "y":
                        liked = True
                    elif response == "n":
                        liked = False
                    # skip and empty default to None (no opinion)
                    
                    feedback_list.append({
                        "question_index": idx - 1,
                        "question_text": question["question"],
                        "liked": liked,
                        "correct": was_correct
                    })
                    break
                print("Please enter 'y', 'n', or 'skip'")
        
        return feedback_list
    
    def run_quiz(self, questions, difficulty):
        """Run the quiz"""
        print(f"\nStarting quiz with {len(questions)} {difficulty} questions...")
        print("="*50)
        
        self.all_feedback = []  # Reset feedback for this quiz
        
        for idx, question in enumerate(questions, 1):
            self.current_question_num = idx
            
            # Validate question type
            q_type = question.get("type")
            if q_type not in VALID_QUESTION_TYPES:
                print(f"Error: Invalid question type '{q_type}'. Skipping question.")
                continue
            
            # Ask question based on type
            if q_type == "multiple_choice":
                user_answer = self.ask_multiple_choice(question)
            elif q_type == "true_false":
                user_answer = self.ask_true_false(question)
            else:  # short_answer
                user_answer = self.ask_short_answer(question)
            
            # Check answer
            correct = self.check_answer(user_answer, question["answer"])
            
            if correct:
                print("✓ Correct!")
                self.streak += 1
                self.multiplier = STREAK_MULTIPLIER ** (self.streak - 1)
                score_gain = self.calculate_score_gain(difficulty)
                self.score += score_gain
                print(f"You earned {score_gain} points (Streak: {self.streak}x, Multiplier: {self.multiplier:.2f})")
            else:
                print(f"✗ Incorrect! The correct answer is: {question['answer']}")
                self.streak = 0
                self.multiplier = 1.0
                print("Streak reset!")
            
            # Store correctness for this question (feedback will be collected later)
            self.all_feedback.append({
                "question_index": idx - 1,
                "correct": correct,
                "user_answer": user_answer,
                "correct_answer": question["answer"]
            })
            
            print(f"Current Score: {self.score}")
        
        print("\n" + "="*50)
        print(f"Quiz Complete! Final Score: {self.score}")
        print("="*50)
        
        # Ask for feedback on all questions at the end
        feedback_data = self.ask_batch_feedback(questions)
        
        # Save score to history with all feedback
        self.user_manager.save_score(self.score, len(questions), difficulty, feedback_data=feedback_data)
        
        # Update user preferences based on feedback
        self.user_manager.update_user_preferences(feedback_data)
    
    def show_stats(self):
        """Display user statistics"""
        stats = self.user_manager.get_stats()
        if isinstance(stats, str):
            print(f"\n{stats}")
        else:
            print("\n" + "="*50)
            print("YOUR STATISTICS")
            print("="*50)
            print(f"Total Quizzes Completed: {stats['total_quizzes']}")
            print(f"Total Score: {stats['total_score']}")
            print(f"Average Score: {stats['average_score']}")
            print(f"Best Score: {stats['best_score']}")
            print("="*50)
    
    def run(self):
        """Main application loop"""
        try:
            # Authenticate user
            self.authenticate_user()
            
            # Show welcome message once
            print("\n" + "="*50)
            print(f"Welcome, {self.user_manager.current_user}!")
            print("="*50)
            
            while True:
                menu_choice = input("\n1. Take a Quiz\n2. View Statistics\n3. Exit\nChoose an option (1-3): ").strip()
                
                if menu_choice == "1":
                    # Reset score and streak for new quiz
                    self.score = 0
                    self.streak = 0
                    self.multiplier = 1.0
                    
                    # Get quiz parameters
                    num_questions = self.get_num_questions()
                    difficulty = self.get_difficulty()
                    
                    # Get filtered questions
                    filtered_questions = self.get_filtered_questions(difficulty, num_questions)
                    
                    if filtered_questions:
                        self.run_quiz(filtered_questions, difficulty)
                
                elif menu_choice == "2":
                    self.show_stats()
                
                elif menu_choice == "3":
                    print("Thank you for using the 15-112 Quiz Application. Goodbye!")
                    break
                
                else:
                    print("Invalid option. Please enter 1, 2, or 3.")
        
        except KeyboardInterrupt:
            print("\n\nApplication interrupted. Goodbye!")
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading data: {e}")
        except ValueError as e:
            print(f"Invalid input error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    quiz_app = Quiz()
    quiz_app.run()
