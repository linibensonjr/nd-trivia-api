import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from random import randrange

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


# Set up pagination
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
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    # An endpoint to handle GET requests
    @app.route('/categories', methods=['GET'])
    def get_categories():
        all_categories = Category.query.all()
        total_categories = len(avail_categories)
        avail_categories = {}
        for category in all_categories:
            avail_categories[category.id] = category.type

        return jsonify({
            'success': True,
            'categories': avail_categories,
            'total_categories': total_categories,
        })


    #Request for questions, including pagination (every 10 questions).
    @app.route('/questions', methods=['GET'])
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        total_questions = len(questions)
        all_questions = paginate(request, questions)

        if (len(all_questions) == 0):
            abort(404)

        all_categories = Category.query.all()
        avail_categories = {}
        for category in all_categories:
            avail_categories[category.id] = category.type
        
            for question in questions:
                question_category = question.category
       

        return jsonify({
            'success': True,
            'questions': all_questions,
            'current_category': question_category,
            'total_questions': total_questions,
            'categories': avail_categories,  
        })


   # Delete question
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none() 
            
            if question is None:
                abort(404)

            question.delete()

            return jsonify({
                    'success': True,
                    'deleted': question_id,
                    'message': 'Question Deleted',          
                })
        except:
            abort(422)


    # Add new question
    @app.route('/questions', methods=['POST'])
    def new_question():
        body = request.get_json()

        question = body.get('question', None)
        answer = body.get('answer', None) 
        difficulty = body.get('difficulty', None)
        category = body.get('category', None)

        try:
            question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_question = paginate(request, selection)

            return jsonify({
                'success': True,
                'created': question.id,
                'questions': current_question,
                'total_question': len(Question.query.all())    
                })
        except:
            abort(422)
            

    # Search for questions
    @app.route('/search', methods=['POST'])
    def search_question():
        body = request.get_json()

        search_term = body.get('searchTerm')
        selection = Question.query.filter(Question.question.ilike('%'+search_term+'%')).all()
        total_questions = len(selection)
        
        if selection:
            current_questions = paginate(request, selection)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': total_questions,
            })
        else:
            abort(404)


    # Get questions based on category.
    @app.route('/categories/<int:cat_id>/questions')
    def questions_per_category(cat_id):
        try:
            category = Category.query.filter_by(id=cat_id).one_or_none()
            selection = Question.query.filter_by(category=cat_id).all()
            total_questions = len(selection)
            current_questions = paginate(request, selection)
            total_questions = len(selection)
            return jsonify({
                'success': True,
                'questions': current_questions,
                'current_category': category.type,
                'total_questions': total_questions,
            })
        except:
            abort(404)
   
   # Endpoint for running the quiz
    @app.route('/quizzes', methods=['POST'])
    def start_quiz():
        
        body = request.get_json()

        # Store ids previous questions
        previous_questions = body.get('previous_questions')
        category = body.get('quiz_category')

        print("Previous questions", previous_questions)

        if (previous_questions == None) or (category == None):
            abort(400)
        
        try:
            # Get questions from "ALL" categories
            if (category['id'] == 0):
                get_questions = Question.query.all()
                formatted_questions = [question.format() for question in get_questions]
                # print(formatted_questions)

            else:
                # Get questions from selected category
                get_questions = Question.query.filter_by(category=category['id']).all()
                formatted_questions = [question.format() for question in get_questions]

            question_count = len(formatted_questions)
            # print("Formatted Question", formatted_questions)

            # Setup a random question
            randomizer = randrange(0, question_count, 1)
            for question in formatted_questions:
                if question['id'] not in previous_questions:
                    question_queue = formatted_questions[randomizer]
            # print("Queue", question_queue)
            if (len(previous_questions) == question_count):
                return jsonify({"success":True})

            return jsonify ({
                        "success": True,
                        "question": question_queue})
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
            'message': 'Unprocessable'
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            'error': 500,
            "message": "Internal server error"
        }), 500

    return app

