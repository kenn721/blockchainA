import datetime
import json
import uuid

import requests
from flask import render_template, redirect, request, session ,g
from flask_jwt import jwt_required, current_identity, _jwt

from app import app
from app.models.users import User

# The node with which our application interacts, there can be multiple
# such nodes as well.
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"
APP_ADDRESS = 'http://127.0.0.1:5000'

posts = []
answers = []
reviews = []
payments = []

def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        post_content, ans_content, rev_content, pay_content = [], [], [], []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                if tx["type"] == 'post':
                    post_content.append(tx)
                elif tx["type"] == 'answer':
                    ans_content.append(tx)
                elif tx["type"] == 'review':
                    rev_content.append(tx)
                else:
                    pay_content.append(tx)

        global posts, answers ,reviews, payments
        posts = sorted(post_content, key=lambda k: k['timestamp'],
                       reverse=True)
        answers = sorted(ans_content, key=lambda k: k['timestamp'],
                        reverse=True)
        reviews = sorted(rev_content, key=lambda k: k['timestamp'],
                        reverse=True)
        payments = sorted(pay_content, key=lambda k: k['timestamp'],
                        reverse=True)

@app.route('/')
def index():
    fetch_posts()
    return render_template('index.html',
                           title='Skill sharing',
                           posts=posts,
                           user=g.user,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)

@app.route('/user/<int:user_id>')
def user_detail(user_id):
    fetch_posts()
    user = User.query.filter(User.id==user_id).first()
    post,answer,review = [],[],[]
    for i in range(len(reviews)):
        if reviews[i]['author_id']==user_id:
            review.append(reviews[i])
    for i in range(len(posts)):
        if posts[i]['author_id']== user_id:
            post.append(posts[i])
    for i in range(len(answers)):
        if answers[i]['author_id'] == user_id:
            a = answers[i]
            a['reviews'] = []
            for j in range(len(review)):
                if review[j]['ans_id']==answers[i]['id'] and review[j]['post_id'] == answers[i]['post_id']:
                    a['reviews'].append(review[j])
            answer.append(a)
    pay,get = 0,0
    for i in range(len(payments)):
        if payments[i]['pay_to'] == user_id:
            pay += int(payments[i]['content'])
        if payments[i]['pay_user_id'] == user_id:
            get += int(payments[i]['content'])
            
    return render_template('user_detail.html',
                            user=user,
                            posts=post,
                            answers=answer,
                            pay = pay,
                            get = get,
                            readable_time=timestamp_to_string,
                            )

@app.route('/posts/<string:post_id>')
def post_detail(post_id):
    post = None
    for i in range(len(posts)):
        if posts[i]['id'] == post_id:
            post = posts[i]
    return render_template('post_detail.html',
                           title=post['title'],
                           content=post['content'],
                           post_id = post_id,
                           user = g.user,
                           author=post['author'])

@app.route('/post_submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application.
    """
    post_content = request.form["content"]
    title = request.form["title"]
    money = request.form["money"]

    post_object = {
        'id': str(uuid.uuid4()),
        'author': g.user.username,
        'author_id': g.user.id,
        'title': title,
        'content': post_content,
        'money': money,
        'type': 'post',
    }

    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    return redirect('/')

@app.route('/posts/<string:post_id>/create_answer')
def create_answer(post_id):
    return render_template('create_answer.html',
                           title='add answer',
                           user = g.user.username,
                           post_id = post_id)

@app.route('/posts/<string:post_id>/answers')
def answer_list(post_id):
    ans = []
    for i in range(len(answers)):
        if answers[i]['post_id'] == post_id:
            ans.append(answers[i])
    return render_template('answers.html',
                           title='answers',
                           user = g.user,
                           post_id = post_id,
                           ans_len = len(answers),
                           answers=ans,
                           readable_time=timestamp_to_string)

@app.route('/posts/<string:post_id>/answers/<string:answer_id>', methods=['POST'])
def answer_detail(post_id,answer_id):
    for i in range(len(answers)):
        if answers[i]['post_id'] == post_id:
            if answers[i]['id'] == answer_id:
                answer = answers[i]
    for i in range(len(posts)):
        if posts[i]['id'] == post_id:
            post = posts[i]
    if g.user:
            # Submit a transaction
        new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)
        post_object = {
            'pay_to': answer['author_id'],
            'pay_user_id': g.user.id,
            'title': 'payment',
            'content': post['money'],
            'type': 'payment',
        }
        requests.post(new_tx_address,
            json=post_object,
            headers={'Content-type': 'application/json'})

        return render_template('answer_detail.html',
                           title=answer['title'],
                           content=answer['content'],
                           user = g.user,
                           author=answer['author'],
                           answer_id=answer['id'],
                           post_id=answer['post_id'])
    else:
        return render_template('please_login.html')

@app.route('/posts/<string:post_id>/add_answer', methods=['POST'])
def add_answer(post_id):
    content = request.form["content"]

    post_object = { 
        'id': str(uuid.uuid4()),
        'title': 'answer',
        'content':content,
        'author':g.user.username,
        'author_id': g.user.id,
        'post_id': post_id,
        'type': 'answer',
    }

    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    return redirect('/posts/{}'.format(post_id))

@app.route('/posts/<string:post_id>/<string:answer_id>/create_review',methods=['POST'])
def create_review(post_id, answer_id):
    content = request.form["content"]
    star = request.form["star"]

    ans = None
    for i in range(len(answers)):
        if answers[i]['post_id'] == post_id:
            if answers[i]['id'] == answer_id:
                ans = answers[i]

    post_object = { 
        'title': ans['title'],
        'content':content,
        'author':g.user.username,
        'author_id': g.user.id,
        'ans_id': answer_id,
        'post_id': post_id,
        'star': star,
        'type': 'review',
    }

    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    return redirect('/posts/{}/answers'.format(post_id))


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')