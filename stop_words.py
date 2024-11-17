import nltk
from nltk.corpus import stopwords

# Download the stopwords dataset
nltk.download('stopwords')

# Get the list of English stop words
stop_words = stopwords.words('english')

# Write the stop words to a file
with open('data/stop_words.txt', 'w') as file:
    for word in stop_words:
        file.write(word + '\n')