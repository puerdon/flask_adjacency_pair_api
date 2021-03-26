from nltk import FreqDist
from nltk.util import ngrams

import re


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


    if len_of_string == 1:
        return 0

    else:
        r = list()

        for i, w in enumerate(l):
            if w == substring:
                r.append((i / len_of_string) * (len_of_string / (len_of_string - 1)))

        # print(r)
        return round(sum(r) / len(r), 2)


def get_word_position_in_a_sentence(word, content):
	
	sentences = re.split('[。 ?？!！]', content)

	for sentence in sentences:
		if word in sentence:
			try:
				yield find_substring_indice_in_a_string(sentence, word)
			except:
				# print(sentence)
				# print(word)
				pass


def calculate_word_position_distribution(position_list):
	
	result = {
		"initial": 0,
		"middle": 0,
		"end": 0
	}

	INITIAL_THRESHOLD = 0.3
	END_THRESHOLD = 0.7

	for position in position_list:
		if position <= INITIAL_THRESHOLD:
			result['initial'] += 1
		elif position >= END_THRESHOLD:
			result['end'] += 1
		else:
			result['middle'] += 1

	total = sum(result.values())

	result['initial'] = round(result['initial']/total, 2)
	result['middle'] = round(result['middle']/total, 2) 
	result['end'] = round(result['end']/total, 2) 

	return result

def generate_n_gram_freq_dist(content, freq_dist, n):
	grams = ngrams(content, n)
	freq_dist.update(grams)
	return freq_dist

def change_tuple_dict_key_to_str_dict_key(freq_list):
	result = []
	for ngrams, freq in freq_list:
		result.append({'ngram': '|'.join(ngrams), 'freq': freq})

	return result