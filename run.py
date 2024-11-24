from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('API_KEY')

app = Flask(__name__, static_folder='app/static', template_folder='app/templates')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Comment model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    position = db.Column(db.String(120))
    comment = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Comment {self.name}>"

# Create the database tables (if not already created)
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    category = 'amazing' # Choose one of the categories from the API docs
    api_url = 'https://api.api-ninjas.com/v1/quotes?category={}'.format(category)
    response = requests.get(api_url, headers={'X-Api-Key': API_KEY})
    if response.status_code == requests.codes.ok:
        resp = response.json()
        first_quote = resp[0]['quote']
    else:
        print("Error:", response.status_code, response.text)
        first_quote = "Loading ..."
    comments = Comment.query.all()
    return render_template('index.html', comments=[{'NAME': c.name, 'POSITION': c.position, 'COMMENT': c.comment} for c in comments], amazing_quote=first_quote)

@app.route('/add_comment', methods=['POST'])
def add_comment():
    name = request.form['name']
    position = request.form['position']
    comment_text = request.form['comment']

    new_comment = Comment(name=name, position=position, comment=comment_text)
    db.session.add(new_comment)
    db.session.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)