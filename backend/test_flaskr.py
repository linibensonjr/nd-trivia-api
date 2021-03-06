import os
from sys import dllhandle
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flaskr import create_app
from models import setup_db, Question, Category


load_dotenv()
class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = os.getenv("DATABASE")
        self.database_username = os.getenv("USER")
        self.database_pwd = os.getenv("PWD")
        self.database_host = os.getenv("HOST")
        self.database_path = "postgresql://{}:{}@{}/{}".format(self.database_username, self.database_pwd, self.database_host, self.database_name)
        setup_db(self.app, self.database_path)

        self.test_question = {
                    "question": "When was Jerusalem destroyed by the Babylonians",
                    "answer": "587 BCE",
                    "category": "4",
                    "difficulty": "4"
                }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])


    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["categories"])


    def test_404_page_not_found(self):
        res = self.client().get('/questions?page=500')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], 'Not Found')


    def test_delete_question(self):
        res = self.client().delete('/questions/13')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 13)


    def test_422_if_question_does_not_exist(self):
        res = self.client().delete('/questions/1500')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable")


    def test_add_question(self):
        add_question = {
            'question': 'What is the most popular cyptocurrency?',
            'answer': 'Bitcoin',
            'difficulty': '1',
            'category': '4'
        }
        res = self.client().post('/questions', json=add_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])

    def test_405_unable_to_add_question(self):
        res = self.client().post('/questions/34', json=self.test_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Method Not Allowed")


    def test_search(self):
        search = {'searchTerm': 'Which'}
        res = self.client().post('/search', json=search)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data["questions"])
        self.assertEqual(len(data['questions']), 7)


    def test_search_not_found(self):
        search = {'searchTerm': 'someterm'}
        res = self.client().post('/search', json=search)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)


    def test_start_quiz(self):
        quiz_question = {'previous_questions': [],'quiz_category': {
                'type': 'Sports',
                'id': 6}
        }
        res = self.client().post('/quizzes', json=quiz_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

        self.assertEqual(data['question']['category'], 6)
        self.assertEqual(data['question']['id'], 10)
        

    def test_404_start_quiz(self):
        quiz_question = {'previous_questions': [7],
            'quiz_category': {
                'type': 'Historia',
                'id': '9'}
        }
        res = self.client().post('/quizzes', json=quiz_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()