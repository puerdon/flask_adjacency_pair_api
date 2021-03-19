import os
from collections import Counter

from flask import Flask, jsonify, request
from flask_cors import CORS

import pickle
import re

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

    key = {
        "initiator": "comment",
        "replier": "recomment",
        "both": "both"
    }
    
    # 如果有指定 推/噓/箭頭
    if comment_type is not None:
    
        for pair in corpus:
            if pair['comment_type'] == comment_type and (word in pair[key[which_side] + '_content']):
                result['data'].append(pair)
                author_counter[pair[key[which_side] + '_user']] += 1
    
    # 如果沒有            
    else:

        # 選兩邊都出現的
        if which_side == 'both':

            for pair in corpus:

                if word in pair['comment_content'] and word in pair['recomment_content']:
                    pair['comment_content_position'] = find_substring_indice_in_a_string(pair['comment_content'], word)
                    pair['recomment_content_position'] = find_substring_indice_in_a_string(pair['recomment_content'], word)
                    result['data'].append(pair)
                    author_counter[pair['comment_user']] += 1
                    author_counter[pair['recomment_user']] += 1

        else:
            position_list = list()
            for pair in corpus:
                utterance = pair[key[which_side] + '_content']
                if word in utterance:
                    try:
                        word_position = find_substring_indice_in_a_string(utterance, word)
                    except:
                        print(utterance)
                    position_list.append(word_position)                
                    # pair[key[which_side] + '_content'] += ' || ' + str(word_position)
                    pair[key[which_side] + '_content_position'] = word_position
                    result['data'].append(pair)
                    author_counter[pair[key[which_side] + '_user']] += 1

            result['statistics']['word_position'] = round(sum(position_list) / len(position_list), 2)


    print(result['statistics'])
    result['statistics']['total'] = sum(author_counter.values())
    result['statistics']['author_type'] = len(author_counter.keys())

    if result['statistics']['total'] == 0:

        result['statistics']['author_diversity'] = 0
    else:
        result['statistics']['author_diversity'] = round(result['statistics']['author_type'] / result['statistics']['total'], 2)
    
    return jsonify(result)

def find_substring_indice_in_a_string(string, substring):

    l = list()

    list_of_words_without_keyword = string.split(substring)

    for _i, _w in enumerate(list_of_words_without_keyword):

        l += list(_w)
        
        if _i == len(list_of_words_without_keyword) - 1:
            continue
        
        else:
            l.append(substring)



    len_of_string = len(l)

    r = list()

    for i, w in enumerate(l):
        if w == substring:
            r.append((i / len_of_string) * (len_of_string / (len_of_string - 1)))

    print(r)
    return round(sum(r) / len(r), 2)

#we define the route /
@app.route('/')
def welcome():
    # return a json
    return jsonify({'status': 'api working'})

@app.route('/query')
def query():
    query_word = request.args.get("word")
    comment_type = request.args.get("comment_type", None)
    which_side = request.args.get("which_side")
    return query_word_from_side(query_word, which_side, comment_type)

# @app.route('/recomment')
# def recomment():
#     query_word = request.args.get("word")
#     comment_type = request.args.get("comment_type", None)
#     return query_word_from_side(query_word, "recomment", comment_type)

if __name__ == '__main__':
    #define the localhost ip and the port that is going to be used
    # in some future article, we are going to use an env variable instead a hardcoded port 
    app.run(host='0.0.0.0', port=os.getenv('PORT'))

