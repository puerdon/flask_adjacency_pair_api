import os
from collections import Counter

from flask import Flask, jsonify, request
from flask_cors import CORS

import pickle

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

with open("womentalk_2019_pair.pickle", "rb") as f:
    corpus = pickle.load(f)

def query_word_from_side(word, which_side, comment_type=None):
    
    author_counter = Counter()
    
    result = {
        "statistics": {
            "total": 0,
            "author_type": 0,
            "author_diversity": 0
        },
        "data": []
    }
    
    if comment_type is not None:
    
        for pair in corpus:
            if pair['comment_type'] == comment_type and (word in pair[which_side + '_content']):
                result['data'].append(pair)
                author_counter[pair[which_side + '_user']] += 1
                
    else:
        for pair in corpus:
            if word in pair[which_side + '_content']:
                result['data'].append(pair)
                author_counter[pair[which_side + '_user']] += 1
                
    result['statistics']['total'] = sum(author_counter.values())
    result['statistics']['author_type'] = len(author_counter.keys())
    result['statistics']['author_diversity'] = result['statistics']['author_type'] / result['statistics']['total']
    
    
    return jsonify(result)

#we define the route /
@app.route('/')
def welcome():
    # return a json
    return jsonify({'status': 'api working'})

@app.route('/comment')
def comment():
    query_word = request.args.get("word")
    comment_type = request.args.get("comment_type", None)
    return query_word_from_side(query_word, "comment", comment_type)

@app.route('/recomment')
def recomment():
    query_word = request.args.get("word")
    comment_type = request.args.get("comment_type", None)
    return query_word_from_side(query_word, "recomment", comment_type)

if __name__ == '__main__':
    #define the localhost ip and the port that is going to be used
    # in some future article, we are going to use an env variable instead a hardcoded port 
    app.run(host='0.0.0.0', port=os.getenv('PORT'))

