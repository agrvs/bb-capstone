FROM python:3
ARG bucket
ENV BUCKET=$bucket
ADD data_process.py /
ADD requirements.txt /
ADD nlp_utils.py /
RUN pip install -r requirements.txt
CMD ["python", "./data_process.py"]