import cv2
import numpy as np
from PIL import Image
from keras import models
import os
import tensorflow as tf

keras_model_path = "tf_mnist_model2.h5"
model = models.load_model(keras_model_path)

video = cv2.VideoCapture(2)

while True:
    _, frame = video.read()
    im=Image.fromarray(frame, 'RGB')
    im2 = im.resize((28,28))
    im2 = im2.convert('L')
    im2 = np.array(im2)
    im2 = im2/255.0
    
    print(type(im2))
    print(im2.shape)
    np.reshape(im2, (28,28))

    print(model.summary())

    im2=im2.reshape((-1, 28, 28))
    print(im2.shape)
    prediction = model(im2).numpy()
    print(prediction)
    prob = tf.nn.softmax(prediction).numpy()
    print(prob)

    predicted_digit = np.argmax(prob)
    print(predicted_digit)

    key=cv2.waitKey(1000) & 0xFF

    if key == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
