'''NTM SageMaker Processing Job

This is the python code for a SageMaker Processing Job that calculates
the vocabulary file and corpus from a training dataset. Then converts
training data, test data, and validation data into RecordIO Protobuf
format for better performance when training a model.

Author:
    - Alex Graves (1Strategy)
'''

import os
import boto3
import nltk
from io import StringIO
import pandas as pd
import numpy as np
import nlp_utils as nlpu
import sagemaker.amazon.common as smac
from sklearn.feature_extraction.text import CountVectorizer


s3 = boto3.resource('s3')
bucket = os.getenv('BUCKET')
print(f"Using bucket: {bucket}")
prefix = "prepared"
nltk.download('wordnet')

# Data Prep
max_freq = 0.9
min_freq = 0.01

# read in datasets and convert to proper type for Vectorizing
train = pd.read_csv(f"s3://{bucket}/{prefix}/train.csv", header=None)
train = train[0].to_numpy()

test = pd.read_csv(f"s3://{bucket}/{prefix}/test.csv", header=None)
test = test[0].to_numpy()

val = pd.read_csv(f"s3://{bucket}/{prefix}/validation.csv", header=None)
val = val[0].to_numpy()

demo = pd.read_csv(f"s3://{bucket}/{prefix}/demo.csv", header=None)
demo = demo[0].to_numpy()

vectorizer = CountVectorizer(input='content',
                            analyzer='word',
                            stop_words='english',
                            tokenizer=nlpu.Lemmatizer(),
                            max_df=max_freq,
                            min_df=min_freq,
                            dtype=np.float32)


# fit_transform() will help create our vocab list
#   we only need to transform() the other datasets.
#   we don't want to polute the vocab list with additional
#   words that won't be used to train on.
train_vectorized = vectorizer.fit_transform(train)
val_vectorized = vectorizer.transform(val)
test_vectorized = vectorizer.transform(test)
demo_vectorized = vectorizer.transform(demo)

del(train)
del(val)
del(test)
del(demo)

vocab = vectorizer.get_feature_names()
print(f"Vocabulary size: {len(vocab)} words")
print(f"Train Shape: {train_vectorized.shape}")
print(f"Validate Shape: {val_vectorized.shape}")
print(f"Test Shape: {test_vectorized.shape}")

# upload vocab file to S3
vocab_file = StringIO("\n".join(vocab))
s3.Object(bucket, f"processed/vocab.txt").put(Body=vocab_file.getvalue())

# upload training set
try:
    nlpu.recordize(train_vectorized, bucket, f"processed/train", parts=12)
except Exception as e:
    print(e)

# upload validation set
try:
    nlpu.recordize(val_vectorized, bucket, f"processed/validation", parts=1)
except Exception as e:
    print(e)

# upload test set
try:
    nlpu.recordize(test_vectorized, bucket, f"processed/test", parts=1)
except Exception as e:
    print(e)

# upload demo set
try:
    demo_buffer = StringIO()
    demo_df = pd.DataFrame(demo_vectorized.toarray())
    demo_df.to_csv(demo_buffer, index=False, header=False)
    s3.Object(bucket, f"processed/demo.csv").put(Body=demo_buffer.getvalue())

except Exception as e:
    print(e)