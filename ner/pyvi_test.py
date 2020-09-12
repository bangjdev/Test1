import json
import unicodedata
import nltk
from nltk.corpus import stopwords as sw
from pyvi import ViTokenizer, ViPosTagger


def clean_text(text, stopwords):
    res = []

    for word in text.split(" "):
        is_stopword = False
        for stopword in stopwords:
            if (stopword == word.lower()):
                is_stopword = True
                break
        if not is_stopword:
            res += [word]


    return " ".join(res)


def extract_name(text, stopwords):
    tokenized_text = ViTokenizer.tokenize(text)
    tokenized_text = clean_text(tokenized_text, stopwords)
    words, tags = ViPosTagger.postagging(tokenized_text)

    res = []

    for i in range(len(words)):
        if (tags[i] == "Np"):
            # print(words[i])
            res.append(words[i].replace("_", " "))

    return res


nltk.download('stopwords')

with open("vietnamese_stop_words.txt", encoding="utf-8") as stopwords_file:
    stopwords = stopwords_file.readlines()

    for i in range(len(stopwords)):
        stopwords[i] = stopwords[i].strip()

stopwords += sw.words('english')

results = set()

with open('results.json', 'r', encoding='utf-8') as json_file:
    books = json.load(json_file)
    for book in books:
        print("Extracting book title \"" + book['title'] + "\"")

        print("  => From description")
        description = unicodedata.normalize("NFD", book['description'])
        extracted_names = extract_name(description, stopwords)
        for name in extracted_names:
            results.add(name)

        book_reviews = book['reviews']
        # From review's content
        for review in book_reviews:
            print("  => Review of " + review['name'])
            review_content = unicodedata.normalize("NFD", review['content'])
            extracted_names = extract_name(review_content, stopwords)
            for name in extracted_names:
                results.add(name)


            # From comments
            comments = review['comments']
            for comment in comments:
                print("    > Reply by " + comment['name'])
                comment_content = comment['content']
                extracted_names = extract_name(comment_content, stopwords)
                for name in extracted_names:
                    results.add(name)


with open('../names', 'w', encoding='utf-8') as names_file:
    for word in results:
        names_file.write(word + "\n")