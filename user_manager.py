import json
import hashlib
import os
from datetime import datetime
import base64

# User data file path
USERS_FILE = "users_data.bin"
SCORES_FILE = "score_history.bin"

class UserManager:
    def __init__(self):
        self.users = self.load_users()
        self.current_user = None
    
    def hash_password(self, password):
        """Hash password using SHA-256 for security"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_users(self):
        """Load users from the encrypted users file"""
        if not os.path.exists(USERS_FILE):
            return {}
        
        try:
            with open(USERS_FILE, 'rb') as f:
                # Read and decode from base64 (obfuscated but not easily readable)
                data = base64.b64decode(f.read()).decode('utf-8')
                return json.loads(data)
        except:
            return {}
    
    def save_users(self):
        """Save users to the encrypted users file"""
        data = json.dumps(self.users)
        with open(USERS_FILE, 'wb') as f:
            # Encode as base64 (obfuscates data but maintains that usernames could be found)
            f.write(base64.b64encode(data.encode('utf-8')))
    
    def register(self, username, password):
        """Register a new user"""
        if username in self.users:
            return False, "Username already exists"
        
        self.users[username] = {
            "password_hash": self.hash_password(password),
            "created_at": datetime.now().isoformat()
        }
        self.save_users()
        return True, "Registration successful"
    
    def login(self, username, password):
        """Login an existing user"""
        if username not in self.users:
            return False, "Username does not exist"
        
        if self.users[username]["password_hash"] != self.hash_password(password):
            return False, "Incorrect password"
        
        self.current_user = username
        return True, f"Welcome back, {username}!"
    
    def load_score_history(self):
        """Load score history for current user"""
        if not self.current_user:
            return []
        
        if not os.path.exists(SCORES_FILE):
            return []
        
        try:
            with open(SCORES_FILE, 'rb') as f:
                data = base64.b64decode(f.read()).decode('utf-8')
                all_scores = json.loads(data)
                return all_scores.get(self.current_user, [])
        except:
            return []
    
    def save_score(self, score, num_questions, difficulty, timestamp=None):
        """Save score to history for current user"""
        if not self.current_user:
            return
        
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        # Load all scores
        all_scores = {}
        if os.path.exists(SCORES_FILE):
            try:
                with open(SCORES_FILE, 'rb') as f:
                    data = base64.b64decode(f.read()).decode('utf-8')
                    all_scores = json.loads(data)
            except:
                all_scores = {}
        
        if self.current_user not in all_scores:
            all_scores[self.current_user] = []
        
        # Add new score record
        all_scores[self.current_user].append({
            "score": score,
            "num_questions": num_questions,
            "difficulty": difficulty,
            "timestamp": timestamp
        })
        
        # Save back to file
        data = json.dumps(all_scores)
        with open(SCORES_FILE, 'wb') as f:
            f.write(base64.b64encode(data.encode('utf-8')))
    
    def get_stats(self):
        """Get statistics for current user"""
        history = self.load_score_history()
        if not history:
            return "No quiz history yet"
        
        total_score = sum(record["score"] for record in history)
        avg_score = total_score / len(history)
        best_score = max(record["score"] for record in history)
        
        return {
            "total_quizzes": len(history),
            "total_score": total_score,
            "average_score": round(avg_score, 2),
            "best_score": best_score
        }
