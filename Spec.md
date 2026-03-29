High level overview:

A command-line quiz app that takes questions regarding CMU's 15-112 from a database and asks them to students. Questions can be short answer, true or false or multiple choice. When students get multiple answers right they will gain a streak multiplier. The base score that students gain will be hard coded based on difficulty, and multiplied by the multiplier. The app should ask the user how many questions they want to be asked and other inputs to change the question type.

Behavior Description:
First the app says: "Hi, how many questions do you want to do today"
Then once the user enters a number between 1 and the total amount of questions in the questions base the app says okay and what difficulty do you want the questions? (Easy/Medium/Hard)

Then based on that the app will filter for questions only in that difficulty and ask questions, wait for a response and track the score. After each question is answer the app should say correct and print the score or incorrect, print the right answer and the score (whenever the question is answered wrong no points are added)

Easy questions are worth 10 points
Medium Questions are worth 20 points
Hard Questions are worth 30 points

For each consecutive question you get right there is a multiplier that is equal to 1.1x previous multiplier.

Save score as a variable

The question bank should be formatted in a .json like this:

{
  "questions": [
    {
      "question": "What keyword is used to define a function in Python?",
      "type": "multiple_choice",
      "options": ["func", "define", "def", "function"],
      "answer": "def",
      "category": "Python Basics"
      "difficulty": "Easy"
    },
    {
      "question": "A list in Python is immutable.",
      "type": "true_false",
      "answer": "false",
      "category": "Data Structures"
      "difficulty": "Medium"
    },
    {
      "question": "What built-in function returns the number of items in a list?",
      "type": "short_answer",
      "answer": "len",
      "category": "Python Basics"
      "difficulty": "Easy"

    }
    {
    "question": "What is the output of print(2 ** 3)?",
      "type": "short_answer",
      "answer": "8",
      "category": "Python Basics",
      "difficulty": "Easy"
    },
    {
      "question": "Which data structure uses key-value pairs?",
      "type": "multiple_choice",
      "options": ["List", "Tuple", "Dictionary", "Set"],
      "answer": "Dictionary",
      "category": "Data Structures",
      "difficulty": "Easy"
    },
    {
      "question": "What does the 'len()' function do in Python?",
      "type": "multiple_choice",
      "options": ["Returns type", "Returns length", "Returns sum", "Returns index"],
      "answer": "Returns length",
      "category": "Python Basics",
      "difficulty": "Easy"
    },
    {
      "question": "In Python, functions can return multiple values.",
      "type": "true_false",
      "answer": "true",
      "category": "Functions",
      "difficulty": "Medium"
    }
  ]
}

Overall should be atleast two files on .py and one .json

.py should handle all the logic, .json should handle the storage of questions

Error Handling:
If the input for the amount of questions isn't a number it should say not a number please input a number

If the .json file doesn't exist say there is no question bank

If there are not enough questions in the difficulty chosen say, please choose a number less than [insert amount of questions in that difficulty]

Core featurs:
A local login system that prompts users for a username and password (or allows them to enter a new username and password). The passwords should not be easily discoverable.

A score history file that tracks performance and other useful statistics over time for each user. This file should not be human-readable and should be relatively secure. (This means someone could look at the file and perhaps find out usernames but not passwords or scores.)

Users should somehow be able to provide feedback on whether they like a question or not, and this should inform what questions they get next.

The questions should exist in their own human-readable .json file so that they can be easily modified. (This lets you use the project for studying other subjects if you wish; all you have to do is generate the question bank.)

Acceptance Criteria:
1) App must initalize and ask how many questions
2) App must ask only that many questions
3) App must not crash if the answer is empty or not an expected answer like T instead of True for a True or False question
4) App must only ask questions from the question bank
5) App must update questions based on student input
6) App must accurately calculate scores and consistently print them