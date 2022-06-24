from crypt import methods
import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate(request, query):

    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    all_questions = [question.format() for question in query]
    return all_questions[start:end]

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    # An endpoint to handle GET requests

    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        avail_categories = {}
        for category in categories:
            avail_categories[category.id] = category.type


        return jsonify({
            'success': True,
            'categories': avail_categories,
            'total_categories': len(avail_categories)
        })


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/questions', methods=['GET'])
    def get_questions():

        # page = request.args.get('page', 1, type=int)
        # start = (page - 1) * QUESTIONS_PER_PAGE
        # end = start + QUESTIONS_PER_PAGE

        questions = Question.query.order_by(Question.id).all()
        all_question = paginate(request, questions)

        all_categories = Category.query.all()
        categories = {}
        for category in all_categories:
            categories[category.id] = category.type
        
        for question in questions:
            question_category = question.category


        return jsonify({
            'success': True,
            'questions': all_question,
            'total_questions': len(questions),
            'current_category': question_category,
            'categories': categories,
            
        })



    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            questions = Question.query.all()
            question = Question.query.filter(Question.id == question_id).one_or_none()
            
            if question == None:
                abort(404)
            
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_question = paginate(request, selection)

            return jsonify({
                    'success': True,
                    'deleted': current_question,
                    'message': 'Question Deleted',
                    'total_questions': len(questions)
                    
                })

        except:
            abort(433)


    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route('/questions', methods=['POST'])
    def new_question():

        body = request.get_json()

        question = body.get('question', None)
        answer = body.get('answer', None) 
        difficulty = body.get('difficulty', None)
        category = body.get('category', None)

        try:
            questions = Question(question=question, answer=answer, 
                                difficulty=difficulty, category=category)
            questions.insert()

            selection = Question.query.order_by(Question.id).one_or_none()
            current_question = paginate(request, selection)

            return jsonify({
                'success': True,
                'created': question.id,
                'questions': current_question,
                'message': 'Question Added',
                    
                })
        except:
            abort(422)
            



    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/search', methods=['POST'])
    def search():
        body = request.get_json()
        search = body.get('searchTerm')
        questions = Question.query.filter(
            Question.question.ilike('%'+search+'%')).all()

        if questions:
            currentQuestions = paginate(request, questions)
            return jsonify({
                'success': True,
                'questions': currentQuestions,
                'total_questions': len(questions)
            })
        else:
            abort(404)


    #Get questions based on category.
    @app.route('/categories/<int:cat_id>/questions')
    def questions_per_category(cat_id):
        
        category = Category.query.filter_by(id=cat_id).one_or_none()
        if category:
            # retrive all questions in a category
            questions_in_cat = Question.query.filter_by(category=str(cat_id)).all()
            currentQuestions = paginate(request, questions_in_cat)

            return jsonify({
                'success': True,
                'questions': currentQuestions,
                'total_questions': len(questions_in_cat),
                'current_category': category.type
            })
        # if category not founs
        else:
            abort(404)
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def quiz():
        
        body = request.get_json()
        quizCategory = body.get('quiz_category')
        previousQuestion = body.get('previous_questions')

        try:
            if (quizCategory['id'] == 0):
                questionsQuery = Question.query.all()
            else:
                questionsQuery = Question.query.filter_by(
                    category=quizCategory['id']).all()

            randomIndex = random.randint(0, len(questionsQuery)-1)
            nextQuestion = questionsQuery[randomIndex]

            stillQuestions = True
            while nextQuestion.id not in previousQuestion:
                nextQuestion = questionsQuery[randomIndex]
                return jsonify({
                    'success': True,
                    'question': {
                        "answer": nextQuestion.answer,
                        "category": nextQuestion.category,
                        "difficulty": nextQuestion.difficulty,
                        "id": nextQuestion.id,
                        "question": nextQuestion.question
                    },
                    'previousQuestion': previousQuestion
                })

        except:
            abort(404)



    # Error handlers for all expected errors

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            'error': 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': '404',
            'message': 'Not Found'
        }), 404

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success': False,
            'error': '405',
            'message': 'Method Not Allowed'
        }), 405

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            'success': False,
            'error': '422',
            'message': 'Unprocessable Entity'
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            'error': 500,
            "message": "Internal server error"
        }), 500

        


    return app

