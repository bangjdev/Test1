words = set()

with open("./names", "r", encoding="utf-8") as file:
	read = file.readlines()

	# eliminate word that is a part of other words
	for word in read:
		sub_word = False
		for another_word in read:
			if len(word.strip()) < len(another_word.strip()):
				print(word.strip(), " === ", another_word.strip())
				if word.strip().lower() in another_word.strip().lower():
					sub_word = True
					break

		if not sub_word:
			words.add(word.strip())


with open("./names_no_dups.txt", "w", encoding="utf-8") as file:
	for word in words:
		file.write(word + "\n")