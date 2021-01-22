'''NTM Data Ingestion Glue Job

This is an AWS Glue Job that reads the Amazon Review data and separates it into
positive reviews and negative reviews. Negative reviews are written to a new location
in S3. Positive reviews are dropped.

Author:
    - Alex Graves (1Strategy)
'''

import sys
from io import StringIO
from awsglue.utils import getResolvedOptions
import boto3
import pandas as pd

# parse arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME', 's3_bucket', 's3_object_key'])
bucket = args['s3_bucket']
key = args['s3_object_key']
print(f"Found bucket: {bucket}\n    and object: {key}")

# read in file that triggered this job
amzn_reviews = pd.read_csv(f"s3://{bucket}/{key}", header=None)
cols = ["pole", "title", "review"]
amzn_reviews.columns = cols

# extract the target review types
target_reviews = amzn_reviews[amzn_reviews.pole == 1]
del(amzn_reviews)

# extract review field as an array and shuffle
input_dataset = target_reviews.review.to_numpy()
del(target_reviews)

# convert array back to DataFrame
input_dataset_df = pd.DataFrame(input_dataset)
del(input_dataset)

# Write to S3
buffer = StringIO()
input_dataset_df.to_csv(buffer, index=False, header=False)
s3 = boto3.resource('s3')
s3.Object(bucket, 'filtered/negative_reviews.csv').put(Body=buffer.getvalue())