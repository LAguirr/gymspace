from flask import Flask, render_template, redirect, url_for, request, flash, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient, ASCENDING
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import re
import base64

app = Flask(__name__)

# Set up the MongoDB client, replace <password> with your actual password.
client = MongoClient('')
# Select the database
db = client['gym']
# Select the collection
collection = db['users']

date = datetime.now() - timedelta(hours=6)


def initialize_user_id_counter():
    counters_collection = db['counters']
    if counters_collection.find_one({'_id': 'user_id'}) is None:
        counters_collection.insert_one({'_id': 'user_id', 'seq': 0})


def get_next_user_id():
    initialize_user_id_counter()
    counters_collection = db['counters']
    # Find and update the counter document, incrementing the user_id value
    counter = counters_collection.find_one_and_update(
        {'_id': 'user_id'},
        {'$inc': {'seq': 1}},
        upsert=True,
        return_document=True
    )

    return counter['seq']


def get_last_user_id():
    counters_collection = db['counters']
    counter = counters_collection.find_one({'_id': 'user_id'})

    return counter['seq'] + 1


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if (username == 'SpaceGym') and (password == '12345'):
            return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/index')
def index():
    return render_template('index.html', date=date)


@app.route('/dashboard')
def dashboard():
    users = collection.find({}).sort('end_date', ASCENDING)

    return render_template('dashboard.html', users=users, date=date)


@app.route('/register', methods=['GET', 'POST'])
def register():

    # Get data from the form
    if request.method == 'POST':
        user_id = get_next_user_id()
        name = request.form['name']
        membership = request.form['membership']
        start_date = request.form.get(
            'start_date', type=lambda x: datetime.strptime(x, '%Y-%m-%d'))
        end_date = request.form.get(
            'end_date', type=lambda x: datetime.strptime(x, '%Y-%m-%d'))

        # Check if the required fields are not null
        if not user_id or not membership or not start_date:
            return jsonify({'error': 'user_id, start_date, and end_date must not be null'}), 400

        photo = request.form['captured_image']
        print(photo)
        if photo != '':
            user = {
                'user_id': user_id,
                'name': name,
                'membership': membership,
                'start_date': start_date,
                'end_date': end_date,
                'photo': photo
            }
        else:
            user = {
                'user_id': user_id,
                'name': name,
                'membership': membership,
                'start_date': start_date,
                'end_date': end_date
            }

        collection.insert_one(user)

        # Redirect to another page, for example, the dashboard or a confirmation page
        return redirect(url_for('dashboard'))
        # return jsonify({'status': 'success', 'message': 'User registered', '_id': str(result.inserted_id)}), 201
    user_id = get_last_user_id()
    # If it's a GET request, render the registration form template
    return render_template('register.html', date=date, user_id=user_id)


@app.route('/delete/<user_id>', methods=['DELETE'])
def delete(user_id):
    # Perform the deletion operation
    result = collection.delete_one({'user_id': user_id})
    if result.deleted_count:
        return redirect(url_for('index'))
    else:
        return jsonify({'status': 'failure', 'message': 'No user found with that ID'}), 404


@app.route('/edit/<user_id>', methods=['GET', 'POST'])
def edit(user_id):
    if request.method == 'GET':
        # Retrieve the user document from MongoDB using the user_id
        user = collection.find_one({'user_id': user_id})
        if user:
            # Render the edit template, passing in the user information
            return render_template('edit_user.html', user=user)
        else:
            # Handle the case where no user was found
            return 'No user found with that ID', 404

    elif request.method == 'POST':
        print(request.form)
        membership = request.form['membership']
        start_date = request.form.get(
            'start_date', type=lambda x: datetime.strptime(x, '%Y-%m-%d'))
        end_date = request.form.get(
            'end_date', type=lambda x: datetime.strptime(x, '%Y-%m-%d'))

        # Check if the required fields are not null
        if not user_id or not membership or not start_date:
            return jsonify({'error': 'user_id, membership, and start_date must not be null'}), 400

        # Insert the new user
        user = {
            'membership': membership,
            'start_date': start_date,
            'end_date': end_date
        }

        # Update user
        collection.update_one({'user_id': user_id}, {'$set': user})

        # return jsonify({'status': 'success', 'message': 'User updated'}), 200
        return redirect(url_for('dashboard'))


@app.route('/search_user', methods=['GET'])
def search_user():
    # Get the user number from the query string
    user = request.args.get('user')

    # Create a regular expression for partial, case-insensitive matching
    regex_pattern = re.compile('.*{}.*'.format(re.escape(user)), re.IGNORECASE)

    # Search in MongoDB database for users matching the query in either user_id or name
    users = collection.find({
        '$or': [
            {'user_id': {'$regex': regex_pattern}},
            {'name': {'$regex': regex_pattern}}
        ]
    })

    if users:
        # If a user is found, render a template with the user data
        return render_template('dashboard.html', users=users, date=date)
    else:
        # If no user is found, you can render a 'not found' template or pass a message
        return render_template('user_not_found.html', message="No se encontro Usuario"), 404


@app.route('/profile/<user_id>', methods=['GET'])
def profile(user_id):

    user = collection.find_one({'user_id': user_id})

    return render_template('user_profile.html', user=user, date=date)


if __name__ == "__main__":
    app.run(debug=False)
