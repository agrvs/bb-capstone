'''NTM Data Preparation Glue Job

This is an AWS Glue Job that reads a source dataset of negative Amazon reviews
and divides it into demo data, validation data, test data, and training data.

Author:
    - Alex Graves (1Strategy)
'''


import sys
from io import StringIO
from awsglue.utils import getResolvedOptions
import random
import boto3
import pandas as pd

# Parse arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME', 's3_bucket', 'train_percent'])
bucket = args['s3_bucket']
train_percent = float(args['train_percent'])
print(f"Starting data preparation job for s3://{bucket}/filtered/negative_reviews.csv")

# Read in data from s3
reviews = pd.read_csv(f"s3://{bucket}/filtered/negative_reviews.csv", header=None)
input_data = reviews[0].to_numpy()

# Shuffle dataset
random.seed(42)
random.shuffle(input_data)

# remove reviews with fewer than 50 words
trimmed_input = [doc for doc in input_data if len(doc) >= 50]
del(input_data)

split = int(train_percent * len(trimmed_input))
remainder_len = len(trimmed_input[split:])//2

# split into train_set, validation_set, and test_set
# extract a few entries as demo data
train_set = trimmed_input[:split]
validation_set = trimmed_input[split:-remainder_len]
test_set = trimmed_input[-remainder_len:-5]
demo_set = trimmed_input[-5:]

print("Lengths:")
print(f"Val   - {len(validation_set)}")
print(f"Train - {len(train_set)}")
print(f"Test  - {len(test_set)}")
print(f"Demo  - {len(demo_set)}")

# Write data to S3
s3 = boto3.resource('s3')
for i, doc in enumerate(demo_set):
    demo_file = StringIO(doc)
    s3.Object(bucket, f"demos/document_{i+1}.txt").put(Body=demo_file.getvalue())

dataset_names = ["train", "validation", "test", "demo"]
for i, dataset in enumerate([train_set, validation_set, test_set, demo_set]):
    buffer = StringIO()
    dataset_df = pd.DataFrame(dataset)
    dataset_df.to_csv(buffer, index=False, header=False)
    s3.Object(bucket, f"prepared/{dataset_names[i]}.csv").put(Body=buffer.getvalue())