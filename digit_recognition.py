from tensorflow.keras.models import load_model
from math import sqrt
import numpy as np
import cv2


class DigitClassifier(object):
    def __init__(self, number_boxes, model_path, probability_treshold=0.8):
        self.number_boxes = number_boxes
        self.model = self.initialize_model(model_path)
        self.probability_treshold = probability_treshold
        self.predicted_digits = list()
        self.number_prediction()


    def __str__(self):
        ret_str = ''
        for row in self.sudoku_board():
            for digit in row:
                ret_str += f'{digit} '
            ret_str += '\n'
        
        return ret_str


    def initialize_model(self, model_path):
        """
        Loads digit recognition model from {model_path}
        """
        model = load_model(model_path)
        return model


    def number_prediction(self):
        """
        Predicts digits from each image in {self.number_boxes}\n
        Saves predicted values in order in {self.predicted_digits}
        """
        for box in self.number_boxes:
            image = self.number_box_preparation(box)
            predicted_digit = self.digit_prediction(image)
            self.predicted_digits.append(predicted_digit)


    def number_box_preparation(self, number_box, shave_pixels=6):
        """
        Adjsuts images in {self.number_boxes} so they work better with digit recognition
        """
        # Sets the image to black and white
        (threshold, image) = cv2.threshold(number_box, 127, 255, cv2.THRESH_BINARY)

        # Inverts color
        # image = 255 - image

        image = np.asarray(image)

        # Removes edges from an image
        image = image[shave_pixels:image.shape[0] - shave_pixels, shave_pixels:image.shape[1] - shave_pixels]

        image = cv2.resize(image, (32, 32))

        # Set range of color values [0.0, 1.0]
        image = image / 255

        image = image.reshape(1, 32, 32, 1)
        
        return image


    def digit_prediction(self, number_box):
        """
        Predicts digit in a {number_box} image\n
        If probability < {self.probability_treshold}: return 0
        """
        predictions = self.model.predict(number_box)

        class_idx = np.argmax(predictions, axis=-1)
        probability = np.amax(predictions)

        if probability > self.probability_treshold:
            return class_idx[0]

        else:
            return 0


    def sudoku_board(self):
        """
        Returns a list of lists containing predicted sudoku board
        """
        sudoku_size = int(sqrt(len(self.predicted_digits)))
        board = [self.predicted_digits[i:i + sudoku_size] for i in range(0, len(self.predicted_digits), sudoku_size)]

        return board