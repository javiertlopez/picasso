import os
import json
import urllib.parse
import boto3
import uuid
import sys
import cv2
import requests
import numpy as numpy
import matplotlib.pyplot as plt

# Create SQS client
sqs = boto3.client('sqs')
s3 = boto3.client('s3')

queue_url = os.environ['SQS_QUEUE']
api_url = os.environ['API_ENDPOINT']

# Receive message from SQS queue
response = sqs.receive_message(
    QueueUrl=queue_url,
    AttributeNames=[
        'SentTimestamp'
    ],
    MaxNumberOfMessages=1,
    MessageAttributeNames=[
        'All'
    ],
    VisibilityTimeout=0,
    WaitTimeSeconds=0
)

message = response['Messages'][0]
receipt_handle = message['ReceiptHandle']

obj = json.loads(message['Body'])

bucket = obj['bucket']
key = obj['key']

other_key = uuid.uuid4()
filename = str(other_key)
with open(filename, 'wb') as f:
    s3.download_fileobj(bucket, key, f)

try:
    # codigo obtenido de aqui
    # https://www.youtube.com/watch?v=rRcwuQGDFOA&t=154s

    # read the image from filesystem, pretty self explanatory
    image = cv2.imread(filename);

    # change the image to gray scale and save it
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # plt.imshow(gray ,cmap='gray')
    # plt.savefig('./imgs2/1-gray-scale.png')


    # apply blur to the image to get rid of the noise and save it
    # parameters:
    #   grayscale image
    #   size of the kernel, i.e. group of pixels to prcess https://stackoverflow.com/questions/16655962/opencv-understanding-kernel, bigger kernel more blurred
    #   standar deviation, if 0 provided is automatically calculated
    blur = cv2.GaussianBlur(gray, (11, 11), 0)
    # plt.imshow(blur, cmap='gray')
    # plt.savefig('./imgs2/2-blurred.png')


    # canny algorithm will detect the edges
    # we used the blurred image to avoid capturing the noise form the original greyscale
    # parameters:
    #   lowerValueThreshold
    #   upperValueThreshold
    #   kernel size of the Sobel filter
    canny = cv2.Canny(blur, 30, 150, 3)
    # plt.imshow(canny, cmap='gray')
    # plt.savefig('./imgs2/3-canny.png')

    # Dilatar el tamanio de los edges para que sean mas notorios
    # parametros
    #   imagen con solo los edges
    #   tamanio del kernel
    #   iteraciones
    dilated = cv2.dilate(canny, (1, 1), iterations = 2)
    # plt.imshow(dilated, cmap='gray')
    # plt.savefig('./imgs2/4-dilated.png')


    # Encontrar los contornos
    #   (cnt, hierarchy)
    # parameters:
    #   imagen con solo edges bien definidadas
    #   constante de solo contornos externos
    #   NONE
    # return:
    #   contour: array with all the pixels that belong to a contour
    (contour, heirachy) = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    os.remove(filename)

    url = api_url + key
    payload = {'count': len(contour)}
    r = requests.patch(url, data=json.dumps(payload))

except Exception as e:
    print(e)
    raise e


# Delete received message from queue
sqs.delete_message(
    QueueUrl=queue_url,
    ReceiptHandle=receipt_handle
)
