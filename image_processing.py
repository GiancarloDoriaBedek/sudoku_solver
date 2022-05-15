import numpy as np
import cv2


class ImageProcessor(object):
    def __init__(self, image_path, image_height=450, image_width=450):
        self.image_path = image_path
        self.image_height = image_height
        self.image_width = image_width
        self.image = self.get_image()
        self.largest_contour = self.get_largest_contour()

    def save_sudoku_image(self):
        """
        Saves a focused image of sudoku into '/temp.jpg' file
        """
        if self.largest_contour.size == 0:
            return None

        self.warp_perspective()

        filename = './resources/temp.jpg'
        cv2.imwrite(filename, self.image)


    def get_image(self):
        """
        Load image from {self.image_path}
        """
        image = cv2.imread(self.image_path)
        image = cv2.resize(image, (self.image_width, self.image_height))
        return image


    def get_image_treshold(self):
        """
        Returns a binary image
        """
        image_gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        image_blur = cv2.GaussianBlur(image_gray, (5, 5), 1)
        image_treshold = cv2.adaptiveThreshold(image_blur, 255, 1, 1, 11, 2)

        return image_treshold


    def get_contours(self):
        """
        Returns a list of all contours in an image
        """
        image_treshold = self.get_image_treshold()
        contours, hierarchy = cv2.findContours(image_treshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours


    def get_largest_contour(self, min_area=50):
        """
        Finds a largest contour in an image
        """
        contours = self.get_contours()
        largest_contour = np.array([])
        max_area = 0

        for contour in contours:
            area = cv2.contourArea(contour)

            # Minimal requirement
            if area > min_area:
                contour_aproximation = self.aproximate_contour(contour)

                # If given contour is a rectangle and bigger than previous
                if area > max_area and len(contour_aproximation) == 4:
                    largest_contour = contour_aproximation
                    max_area = area

        largest_contour = self.reorder_contour_vertices(largest_contour)
        return largest_contour


    def aproximate_contour(self, contour):
        """
        Returns an aproximation of a given contour defined by around 4 vertices
        """
        perimeter = cv2.arcLength(contour, True)
        return cv2.approxPolyDP(contour, 0.02 * perimeter, True)


    def reorder_contour_vertices(self, contour):
        """
        Sets countour verices in order
        """
        vertices = contour.reshape((4, 2))
        ordered_vertices = np.zeros((4, 1, 2), dtype=np.int32)
        add = vertices.sum(1)

        ordered_vertices[0] = vertices[np.argmin(add)]
        ordered_vertices[3] = vertices[np.argmax(add)]

        diff = np.diff(vertices, axis=1)

        ordered_vertices[1] = vertices[np.argmin(diff)]
        ordered_vertices[2] = vertices[np.argmax(diff)]

        return ordered_vertices


    def warp_perspective(self):
        """
        Warps loaded image so the result is a forward facing full sized image of sudoku
        """
        contour_vertices = np.float32(self.largest_contour)

        image_edge_points = [[0, 0], [self.image_width, 0], [0, self.image_height], [self.image_width, self.image_height]]
        warped_image_vertices = np.float32(image_edge_points)

        # Calculate transform matrix to adjust sudoku to the image size
        transform_matrix = cv2.getPerspectiveTransform(contour_vertices, warped_image_vertices)

        # Transform sudoku to the size of the image
        self.image = cv2.warpPerspective(self.image, transform_matrix, (self.image_width, self.image_height))

        # Change image to grayscale
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)


    def split_number_boxes(self, sudoku_size=9):
        """
        Splits image into {sudoku_size} x {sudoku_size} list of lists with\n
        each element containing an image of a single sudoku field"""
        rows = np.vsplit(self.image, sudoku_size)
        boxes = list()

        for row in rows:
            row_boxes = np.hsplit(row, sudoku_size)

            for box in row_boxes:
                boxes.append(box)

        return boxes

