import os
import numpy as np
import pickle
from flask import Flask, request, render_template
from keras.preprocessing.sequence import pad_sequences
from keras.models import load_model
from preprocessing import preprocess_comment
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression

app = Flask(__name__)

# Define the path to the templates directory
template_dir = os.path.abspath('templates')
app.template_folder = template_dir

EMBEDDING_DIM = 16
VOCAB_SIZE_ML = 6336
MAXLEN = 120
OOV_TOKEN = "<OOV>"

models_name = ['Logistic Regression', 'Random Forrest', 'SVM', 'LSTM', 'GRU', 'CONV']
dl = [ 'LSTM', 'GRU', 'CONV']
ml = ['Logistic Regression', 'Random Forrest', 'SVM']

# Load DL models
model_LSTM = load_model('models/LSTM.model.h5')
model_GRU = load_model('models/GRU.model.h5')
model_CONV = load_model('models/conv.model.h5')

# Load ML models
with open('models/lr_classifier.pkl', 'rb') as file:
    lr_classifier = pickle.load(file)
with open('models/rf_classifier.pkl', 'rb') as file:
    rf_classifier = pickle.load(file)
with open('models/svm_classifier.pkl', 'rb') as file:
    svm_classifier = pickle.load(file)

# Load the Tokenizer
with open('models/tokenizer.pkl', 'rb') as file:
    tokenizer = pickle.load(file)

# Load the TF-IDF vectorizer
with open('models/tfidf_vectorizer.pkl', 'rb') as file:
    tfidf_vectorizer = pickle.load(file)

label_map = {
    'Quality': 0,
    'Service': 1,
    'Packing': 2,
    'Shipping': 3
}
inverse_label_map = {v: k for k, v in label_map.items()}

@app.route('/')
def home():
    return render_template('index.html', models = models_name)

@app.route('/Predict another comment')
def predict_another():
    return render_template('index.html', models = models_name)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.form
    print(data)
    new_comment = data['comment']
    selected_model = data['model']
    cleaned_comment = preprocess_comment(new_comment)

    tokenizer.fit_on_texts(cleaned_comment)
    new_comment_seq = tokenizer.texts_to_sequences([cleaned_comment])
    new_comment_padded_DL = pad_sequences(new_comment_seq, maxlen=MAXLEN, padding='post')
    # new_comment_padded_ML = pad_sequences(new_comment_seq, maxlen=VOCAB_SIZE_ML, padding='post')
    new_comment_tfidf = tfidf_vectorizer.transform([cleaned_comment])

    predictions = {}
    for model_name, model in zip(models_name, [lr_classifier, rf_classifier, svm_classifier, model_LSTM, model_GRU, model_CONV]):
    # for model_name, model in zip(models_name, [ model_LSTM, model_GRU, model_CONV]):
        if model_name in dl:
            prediction = model.predict(new_comment_padded_DL)
            predicted_label = np.argmax(prediction, axis=1)[0]
            print(model_name)
            print(np.argmax(prediction))
        elif model_name in ml:
            prediction = model.predict(new_comment_tfidf)
            # predicted_label = np.argmax(prediction)
            # predicted_label = prediction[0]
            predicted_label = label_map[prediction[0]] if isinstance(prediction[0], str) else prediction[0]
            print(model_name)
        predicted_label_name = inverse_label_map[predicted_label]
        predictions[model_name] = predicted_label_name
        print(f"Predicted Label: {predicted_label_name}")
        print(prediction)
        # Print predictions for debugging
        print(f"Model: {model_name}, Prediction: {prediction}, Predicted Label: {predicted_label_name}")

    print(f"All predictions: {predictions}")
    
    return render_template('result.html', comment = new_comment, model = selected_model, prediction = predictions[selected_model], all_predictions=predictions)

if __name__ == '__main__':
    app.run(debug=True)
