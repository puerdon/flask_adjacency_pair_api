import os
from collections import Counter
import pickle
import re

from flask import Flask, jsonify, request
from flask_cors import CORS
from nltk import FreqDist


from .helpers import *

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

with open("womentalk_2019_pair.pickle", "rb") as f:
    corpus = pickle.load(f)

def query_word_from_side(word, which_side, comment_type=None):
    
    n_gram_freq_dist_of_utt_containg_keyword = FreqDist()
    n_gram_freq_dist_of_the_other_utt = FreqDist()

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


        list_of_turn_position_of_word = list()
        list_of_sentence_position_of_word = list()


        # 選任意一邊出現的
        if which_side == 'any':

            for pair in corpus:

                if word in pair['comment_content'] or word in pair['recomment_content']:
                    
                    if word in pair['comment_content']:
                        pair['comment_content_position'] = find_substring_indice_in_a_string(pair['comment_content'], word)
                        list_of_turn_position_of_word.append(pair['comment_content_position'])

                        # 取出關鍵詞在句子中的位置
                        for _position in get_word_position_in_a_sentence(word, pair['comment_content']):
                            list_of_sentence_position_of_word.append(_position)
                        

                        author_counter[pair['comment_user']] += 1
                    
                    if word in pair['recomment_content']:
                        pair['recomment_content_position'] = find_substring_indice_in_a_string(pair['recomment_content'], word)
                        list_of_turn_position_of_word.append(pair['recomment_content_position'])
                        
                        # 取出關鍵詞在句子中的位置
                        for _position in get_word_position_in_a_sentence(word, pair['recomment_content']):
                            list_of_sentence_position_of_word.append(_position)

                        author_counter[pair['recomment_user']] += 1

                    result['data'].append(pair)
                    
                    

        # 選兩邊都出現的
        elif which_side == 'both':

            for pair in corpus:

                if word in pair['comment_content'] and word in pair['recomment_content']:
                    pair['comment_content_position'] = find_substring_indice_in_a_string(pair['comment_content'], word)
                    pair['recomment_content_position'] = find_substring_indice_in_a_string(pair['recomment_content'], word)
                    
                    list_of_turn_position_of_word.append(pair['comment_content_position'])
                    list_of_turn_position_of_word.append(pair['recomment_content_position'])
                    
                    # 取出關鍵詞在句子中的位置
                    for _position in get_word_position_in_a_sentence(word, pair['comment_content']):
                        list_of_sentence_position_of_word.append(_position)
                    for _position in get_word_position_in_a_sentence(word, pair['recomment_content']):
                        list_of_sentence_position_of_word.append(_position)

                    result['data'].append(pair)
                    author_counter[pair['comment_user']] += 1
                    author_counter[pair['recomment_user']] += 1

        # 選回文 or 回回文的
        else:
            
            for pair in corpus:
                utterance = pair[key[which_side] + '_content']
                other_side_utterance =  pair['recomment_content'] if key[which_side] == 'comment' else pair['comment_content']
                
                if word in utterance:
                    try:
                        word_position = find_substring_indice_in_a_string(utterance, word)
                    except:
                        print(utterance)
                    list_of_turn_position_of_word.append(word_position) 
                    
                    # 取出關鍵詞在句子中的位置
                    for _position in get_word_position_in_a_sentence(word, utterance):
                        list_of_sentence_position_of_word.append(_position)

                    # pair[key[which_side] + '_content'] += ' || ' + str(word_position)
                    pair[key[which_side] + '_content_position'] = word_position
                    result['data'].append(pair)
                    author_counter[pair[key[which_side] + '_user']] += 1

                    # 計算 n-gram
                    n_gram_freq_dist_of_utt_containg_keyword = generate_n_gram_freq_dist(utterance, n_gram_freq_dist_of_utt_containg_keyword, 2)
                    n_gram_freq_dist_of_the_other_utt = generate_n_gram_freq_dist(other_side_utterance, n_gram_freq_dist_of_the_other_utt, 2)

            result['statistics']['word_position'] = round(sum(list_of_turn_position_of_word) / len(list_of_turn_position_of_word), 2)
            
            result['statistics']['n_gram_freq_dist_of_utt_containg_keyword'] = change_tuple_dict_key_to_str_dict_key(n_gram_freq_dist_of_utt_containg_keyword.most_common(30))
            result['statistics']['n_gram_freq_dist_of_the_other_utt'] = change_tuple_dict_key_to_str_dict_key(n_gram_freq_dist_of_the_other_utt.most_common(30))

    # print(result['statistics'])
    result['statistics']['total'] = sum(author_counter.values())
    result['statistics']['author_type'] = len(author_counter.keys())
    # print(len(list_of_turn_position_of_word))
    # print(len(list_of_sentence_position_of_word))
    result['statistics']['turn_position_distribution'] = calculate_word_position_distribution(list_of_turn_position_of_word)
    result['statistics']['sentence_position_distribution'] = calculate_word_position_distribution(list_of_sentence_position_of_word)




    if result['statistics']['total'] == 0:

        result['statistics']['author_diversity'] = 0
    else:
        result['statistics']['author_diversity'] = round(result['statistics']['author_type'] / result['statistics']['total'], 2)
    
    return jsonify(result)



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

