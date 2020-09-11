import json
from pyvi import ViTokenizer, ViPosTagger


def clean_text(text, stopwords):
	res = []

	for word in text.split(" "):
		try:
			pos = stopwords[word.lower()]
		except:
			res += [word]


	return " ".join(res)


def extract_name(text):
	tokenized_text = ViTokenizer.tokenize(text)
	tokenized_text = clean_text(tokenized_text, stopwords)
	words, tags = ViPosTagger.postagging(tokenized_text)

	res = []

	for i in range(len(words)):
		if (tags[i] == "Np"):
			print(words[i])
			res.append(words[i])

	return res


with open("vietnamese_stop_words.txt", encoding="utf-8") as stopwords_file:
	stopwords = stopwords_file.readlines()

	for i in range(len(stopwords)):
		stopwords[i] = stopwords[i].strip()


results = set()

with open('../results.json', 'r', encoding='utf-8') as json_file:
    books = json.load(json_file)
    for book in books:
    	description = book['description']
    	extracted_names = extract_name(clean_text(description, stopwords))
    	for name in extracted_names:
    		results.add(name)

with open('../names', 'w', encoding='utf-8') as names_file:
	for word in results:
		names_file.write(word + "\n")