import datetime

import jwt
from flask import request, jsonify
from werkzeug.security import check_password_hash
from app import app, db, auth, bcrypt
from app.UserModel import User
from app.utils import translate_content, translate_content_google
from flask_cors import cross_origin
from app.PostModel import Post
from sqlalchemy.exc import SQLAlchemyError
from flask import abort


@app.route('/translate', methods=['POST'])
@auth.login_required
def translate():
    user = auth.current_user()
    data = request.get_json()
    if not data or 'post_id' not in data or 'content' not in data:
        return jsonify(status='error', message='Missing post_id or content'), 400

    post_id = data['post_id']
    content = data['content']

    # Add new post to database
    new_post = Post(post_id=post_id, content=content, status='Pending')
    db.session.add(new_post)
    db.session.commit()

    # Assuming translate_content updates the post in the database and returns the translated content
    translated_content = translate_content(post_id, content)
    pass
    return jsonify(status='success')


@app.route('/g-translate', methods=['POST'])
@auth.login_required
def gtranslate():
    user = auth.current_user()
    data = request.get_json()
    if not data or 'post_id' not in data or 'content' not in data:
        return jsonify(status='error', message='Missing post_id or content'), 400
    post_id = data['post_id']
    content = data['content']

    # Check if post already exists
    post = Post.query.filter_by(post_id=post_id).first()

    if post is None:
        # Create a new post record if it doesn't exist
        post = Post(post_id=post_id, content=content, status='Pending')
        db.session.add(post)
        db.session.commit()
    else:
        # Update the existing post record
        post.content = content
        post.status = 'Pending'
        db.session.commit()

    translate_content = translate_content_google(post_id, content)
    pass
    return jsonify(status='success')


def get_translation_status(post_id):
    post = Post.query.filter_by(post_id=post_id).first()
    return post.status if post else None


def get_translation(post_id):
    post = Post.query.filter_by(post_id=post_id).first()
    return post.translated_content if post else None


@app.route('/pull-translate', methods=['POST'])
@cross_origin()
@auth.login_required
def pull_translate():
    user = auth.current_user()
    data = request.get_json()
    if not data or 'post_id' not in data:
        return jsonify(status='error', message='Missing post_id'), 400

    post_id = data['post_id']
    status = get_translation_status(post_id)

    if status == 'Translated':
        translated_content = get_translation(post_id)
        if translated_content is not None:
            return jsonify(status='translated', translated_content=translated_content)
        else:
            return jsonify(status='error', message='Translation not found'), 404
    elif status == 'Pending':
        return jsonify(status='pending', message='Translation is pending'), 202
    else:
        return jsonify(status='error', message='Post not found or translation failed'), 404


@app.route('/token', methods=['POST'])
def generate_token():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        abort(400, description='Missing username or password')
    username = data['username']
    password = data['password']
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        # Assuming SECRET_KEY is your secret key
        token = jwt.encode({'user_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
                           app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token})
    return jsonify({'error': 'Invalid username or password'}), 400


@auth.verify_token
def verify_token(token):
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user = User.query.get(data['user_id'])
        if user:
            return user  # valid token and user found
    except jwt.ExpiredSignatureError:
        abort(401, description='Token has expired')
    except jwt.InvalidTokenError:
        abort(401, description='Invalid token')
    except Exception as e:  # Catch any other exceptions
        print(f"An error occurred: {e}")  # Log the error
        abort(401, description='Could not verify token')
    return False


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        abort(400, description='Missing username or password')
    username = data['username']
    password = data['password']
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'User already exists!'}), 409
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password)
    try:
        db.session.add(new_user)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'message': 'Database error', 'error': str(e)}), 500
    return jsonify({'message': 'New user created!'}), 201


@app.errorhandler(401)
def custom_401(error):
    response = jsonify({'error': 'Unauthorized access'})
    response.status_code = 401
    return response
