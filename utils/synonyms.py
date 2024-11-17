import pandas as pd
from nltk.corpus import wordnet
from nltk import pos_tag, word_tokenize, download
from collections import defaultdict
import os


download('averaged_perceptron_tagger', quiet=True)
download('wordnet', quiet=True)

FILE_PATH = "synonyms.txt"

os.chdir('data/')
dataset = pd.read_json('cord-19.json')

all_texts = dataset['abstract'].dropna().tolist() + dataset['title'].dropna().tolist()

word_dict = defaultdict(set)
for desc in all_texts:
    words = word_tokenize(desc)
    nouns = [word.lower() for word, pos in pos_tag(words) if pos in ['NN', 'NNS']]

    for noun in nouns:
        synonyms = {
            lm.name().lower() for syn in wordnet.synsets(noun) for lm in syn.lemmas() if lm.name().lower() != noun
        }
        if synonyms:
            word_dict[noun].update(synonyms)

os.chdir('..')

with open(FILE_PATH, 'w') as f:
    f.writelines([f"{word}, {', '.join(sorted(synonyms))}\n" for word, synonyms in word_dict.items()])
