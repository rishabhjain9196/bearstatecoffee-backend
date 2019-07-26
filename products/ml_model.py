import pickle
import os
from django.conf import settings
from keras.preprocessing.sequence import pad_sequences


def setup():
    # setup will run only once at startup to reduce latency
    file1 = os.path.join(settings.BASE_DIR, 'tokenizer.pickle')
    with open(file1, 'rb') as handle:
        tokenizer = pickle.load(handle)

    file2 = os.path.join(settings.BASE_DIR, 'teamssmartcompose.sav')

    with open(file2, 'rb') as model_file:
        loaded_model = pickle.load(model_file)
        loaded_model._make_predict_function()

    return tokenizer, loaded_model


def generate_text(seed_text, next_words, max_sequence_len, tokenizer, loaded_model):
    output_text = ""
    conf = []
    for _ in range(next_words):
        token_list = tokenizer.texts_to_sequences([seed_text])[0]
        token_list = pad_sequences([token_list], maxlen=max_sequence_len - 1, padding='pre')
        predicted = loaded_model.predict_classes(token_list, verbose=0)
        score = loaded_model.predict_proba(token_list, verbose=0)
        conf.append(score[0][predicted])
        if score[0][predicted] < 0.95:
            break
        output_word = ""
        for word, index in tokenizer.word_index.items():
            if index == predicted:
                output_word = word
                break

        output_text += output_word + " "
        seed_text += " " + output_text

    output_text.strip()
    return output_text, conf
