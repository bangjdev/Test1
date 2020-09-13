import json



words = set()


not_names = []


with open("../dict.json", "r", encoding="utf-8") as json_file:
	not_names_json = json.load(json_file)
	for name in not_names_json:
		not_names += name['words']


with open("./names_no_dups.txt", "r", encoding="utf-8") as file:
	read = file.readlines()

	# eliminate word that is a part of other words
	for word in read:
		sub_word = False
		is_not_name = False
		for another_word in read:
			if len(word.strip()) < len(another_word.strip()):
				print(word.strip(), " === ", another_word.strip())
				if word.strip().lower() in another_word.strip().lower():
					sub_word = True
					break

		for not_name in not_names:
			if word.strip().lower() in not_name.strip().lower():
				is_not_name = True
				break

		if (not sub_word) and (not is_not_name):
			words.add(word.strip())


with open("./names_no_dups_final.txt", "w", encoding="utf-8") as file:
	for word in words:
		file.write(word + "\n")