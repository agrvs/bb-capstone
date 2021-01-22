#! /usr/bin/env bash

type=$1

REGION="us-west-2"

if [[ $type = "platform" ]]
then
    aws cloudformation deploy \
        --profile capstone \
        --capabilities CAPABILITY_NAMED_IAM \
        --parameter-overrides $(cat ./cloudformation/params.ini) \
        --region $REGION \
        --stack-name "agrvs-capstone-platform" \
        --template-file ./cloudformation/capstone_platform.yml
elif [[ $type = "workflow" ]]
then
    aws cloudformation deploy \
        --profile capstone \
        --capabilities CAPABILITY_NAMED_IAM \
        --parameter-overrides $(cat ./cloudformation/params.ini) \
        --region $REGION \
        --stack-name "agrvs-capstone-workflow" \
        --template-file ./cloudformation/capstone_workflow.yml
else
    echo "I didn't understand your input."
    echo "Please try again with 'platform' or 'workflow'"
fi