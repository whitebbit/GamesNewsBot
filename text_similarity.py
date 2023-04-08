import string
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
stopwords = stopwords.words("russian")


def clean_string(text):
     text = "".join([word for word in text if word not in string.punctuation])
     text = text.lower()
     text = " ".join([word for word in text.split() if word not in stopwords])
     return text


def cosine_similarity_vectors(vec1, vec2):
    vec1 = vec1.reshape(1, -1)
    vec2 = vec2.reshape(1, -1)

    return cosine_similarity(vec1, vec2)[0][0]


def get_similarity(sentense):
    cleaned = list(map(clean_string, sentense))
    vectorizer = CountVectorizer().fit_transform(cleaned)
    vectors = vectorizer.toarray()

    return cosine_similarity_vectors(vectors[0], vectors[-1])



