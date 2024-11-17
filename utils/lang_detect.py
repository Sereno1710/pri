from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
import pandas as pd
import os


os.chdir('data/')
data = pd.read_json('cord-19.json')

def detect_language(text):
    if pd.isnull(text):
        return "unknown"
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"

data['detected_language'] = data['abstract'].apply(detect_language)

# Count the unique languages detected
unique_languages = data['detected_language'].value_counts()

print(unique_languages)

data = data[data['detected_language'] == 'en']
unique_languages = data['detected_language'].value_counts()
print(unique_languages)

data = data.drop(columns=['detected_language'])
os.chdir('..')
data.to_csv('covid_dataset_preprocessed.csv', index=False)






