"""Provides an abstraction of the model for the rest of the application.

Provides API for interacting with the trained model, including loading and
preprocessing images, and making predictions.
"""
import os

import numpy as np
import tensorflow as tf
from google.cloud import storage


def preprocess_file(img_path):
    """Loads and preprocesses an image from the full path to the file.

    Given the full path to an image file, loads the image, resizes it to the
    expected input size of the pretrained model, and preprocesses it to the
    format expected by the model (scaling, mean subtraction, RGB to BGR,
    etc. as applicable).

    Args:
        img_path: Full path to the image file.

    Returns:
        A numpy array containing the preprocessed image.
    """
    img = tf.keras.preprocessing.image.load_img(
        img_path, target_size=(224, 224)
    )
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array_preprocessed = preprocess(img_array)

    return img_array_preprocessed


def preprocess(face_image):
    """Preprocesses a numpy array containing a right-sized image of a face.

    Given a numpy array containing an image of a face, preprocesses it to
    the format expected by the model (scaling, mean subtraction, RGB to BGR,
    etc. as applicable).

    Args:
        face_image: A numpy array containing an image of a face, resized to
            the expected input size of the pretrained model.

    Returns:
        A numpy array containing the preprocessed image.
    """
    img_array = np.expand_dims(face_image, axis=0)
    img_array = tf.keras.applications.vgg16.preprocess_input(img_array)

    return img_array


class Model:
    def __init__(self, model_path, config_data, bucket_name):
        self._model = self.load_model(model_path, bucket_name)
        self.labels_text2num = config_data["labels_text2num"]
        self.labels_num2text = {v: k for k, v in self.labels_text2num.items()}

    def predict(self, img_array):
        """Gets predictions from the model for an already-preprocessed image.

        Args:
            img_array: Image as a numpy array, preprocessed to suit the model.

        Returns:
            The model's predictions for the image as a numpy array containing an
            array of the probabilities for each emotion label.
        """
        return self._model.predict(img_array)[0]

    def load_model(self, model_path, bucket_name):
        if bucket_name:
            client = storage.Client()
            bucket = client.get_bucket(bucket_name)
            blobs = bucket.list_blobs(prefix="models/")

        try:
            latest_blob = max(blobs, key=lambda x: x.updated)
            latest_blob.download_to_filename(model_path)
        except:
            print(f"\nNo model found in GCS bucket {bucket_name}")

            return None

        return tf.keras.models.load_model(model_path, compile=True)
