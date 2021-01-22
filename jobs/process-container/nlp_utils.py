"""NLP Project Tools

This is a set of tools for the automated NLP project.
These tools are adapted from the examples here:
    https://github.com/aws/amazon-sagemaker-examples/tree/master/scientific_details_of_algorithms/ntm_topic_modeling

Author:
    - Alex Graves (1Strategy)
"""

# NLP Utils
# A set of utility functions for NLP data preparation.

import boto3
import sagemaker.amazon.common as smac
import scipy
import string
import io
from sklearn.utils import shuffle
from nltk.stem import WordNetLemmatizer


class Lemmatizer(object):
    """
    Lemmatization links words with similar meanings.

    Where Stemming truncates each string to a word root,
    lemmatization converts words with similar definitions
    into a single entry.
    """
    def __init__(self):
        self.wnl = WordNetLemmatizer()
    def __call__(self, doc, min_len=2):
        # lift out punctuation
        clean = "".join([i.lower() for i in doc if i not in string.punctuation])
        # return lemmatized word if length is sufficient
        return [self.wnl.lemmatize(t) for t in clean.split() if len(t) > min_len]


def recordize(matrices, dest_bucket, prefix, fname_template='data_part{}.pbr', parts=2):
    """
    Converts a sparse array to RecordIO format and uploads
    it to S3.
    """

    s3 = boto3.client('s3')
    chunk_size = matrices.shape[0] // parts

    print("Uploading data to S3:")
    for i in range(parts):
        buffer = io.BytesIO()
        start = i * chunk_size
        end = (i + 1) * chunk_size
        if i + 1 == parts:
            end = matrices.shape[0]

        # this function converts each sparse matrix to RecordIO protobuf
        smac.write_spmatrix_to_sparse_tensor(array=matrices[start:end], file=buffer, labels=None)
        buffer.seek(0)

        s3.upload_fileobj(buffer,
                        Bucket=dest_bucket,
                        Key=f"{prefix}/data_part_{i}.pbr")
        print(f"    s3://{dest_bucket}/{prefix}/data_part_{i}.pbr")