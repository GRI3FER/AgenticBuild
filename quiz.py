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

class Quiz:
    def __init__(self):
        self.user_manager = UserManager()
        self.questions = self.load_questions()
        self.score = 0
        self.streak = 0
        self.multiplier = 1.0
        self.current_question_num = 0
    
    def load_questions(self):
        """Load questions from JSON file"""
        if not os.path.exists(QUESTIONS_FILE):
            return None
        
        try:
            with open(QUESTIONS_FILE, 'r') as f:
                data = json.load(f)
                return data.get("questions", [])
        except:
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
                print("not a number please input a number")
    
    def get_difficulty(self):
        """Get difficulty level from user"""
        while True:
            difficulty = input("\nWhat difficulty do you want? (Easy/Medium/Hard): ").strip()
            if difficulty not in ["Easy", "Medium", "Hard"]:
                print("Please enter Easy, Medium, or Hard")
                continue
            return difficulty
    
    def get_filtered_questions(self, difficulty, num_questions):
        """Filter questions by difficulty"""
        if self.questions is None:
            print("there is no question bank")
            return None
        
        filtered = [q for q in self.questions if q["difficulty"] == difficulty]
        
        if num_questions > len(filtered):
            print(f"please choose a number less than {len(filtered)}")
            return None
        
        # Select random questions
        return random.sample(filtered, num_questions)
    
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
        user_input = input("Your answer: ").strip().lower()
        
        if not user_input:
            print("Answer cannot be empty. Please try again.")
            return self.ask_short_answer(question_data)
        
        return user_input
    
    def check_answer(self, user_answer, correct_answer):
        """Check if answer is correct"""
        user_answer = str(user_answer).lower().strip()
        correct_answer = str(correct_answer).lower().strip()
        
        return user_answer == correct_answer
    
    def calculate_score_gain(self, difficulty):
        """Calculate score gain with multiplier"""
        base_points = DIFFICULTY_POINTS[difficulty]
        return int(base_points * self.multiplier)
    
    def run_quiz(self, questions, difficulty):
        """Run the quiz"""
        print(f"\nStarting quiz with {len(questions)} {difficulty} questions...")
        print("="*50)
        
        for idx, question in enumerate(questions, 1):
            self.current_question_num = idx
            
            # Ask question based on type
            if question["type"] == "multiple_choice":
                user_answer = self.ask_multiple_choice(question)
            elif question["type"] == "true_false":
                user_answer = self.ask_true_false(question)
            else:  # short_answer
                user_answer = self.ask_short_answer(question)
            
            # Check answer
            correct = self.check_answer(user_answer, question["answer"])
            
            if correct:
                print("✓ Correct!")
                self.streak += 1
                self.multiplier = 1.1 ** (self.streak - 1)
                score_gain = self.calculate_score_gain(difficulty)
                self.score += score_gain
                print(f"You earned {score_gain} points (Streak: {self.streak}x, Multiplier: {self.multiplier:.2f})")
            else:
                print(f"✗ Incorrect! The correct answer is: {question['answer']}")
                self.streak = 0
                self.multiplier = 1.0
                print("Streak reset!")
            
            print(f"Current Score: {self.score}")
        
        print("\n" + "="*50)
        print(f"Quiz Complete! Final Score: {self.score}")
        print("="*50)
        
        # Save score to history
        self.user_manager.save_score(self.score, len(questions), difficulty)
    
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
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    quiz_app = Quiz()
    quiz_app.run()
