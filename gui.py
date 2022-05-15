import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

from copy import deepcopy

from image_processing import ImageProcessor
from digit_recognition import DigitClassifier
from backtracking import SudokuSolver



class MainApplication(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title('Sudoku Solver')
        self.resizable(False, False)
        self.config(bg='#F9E4D4')

        self.initialize_frames()
        self.place_frames()


    def initialize_frames(self):
        self.main_frame = MainFrame(self)


    def place_frames(self):
        self.main_frame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)


class MainFrame(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.config(bg = '#F9E4D4')
        self.button_setting = {
            'bg': '#9C0F48', 
            'fg': '#F9E4D4', 
            'border': 0, 
            'highlightthickness': 1, 
            'activebackground': '#470D21', 
            'width': 20
            }

        self.chosen_image_path = None

        self.initialize_elements()
        self.place_elements()

        # Set a placeholder image on canvas
        self.load_image('./resources/placeholder.png')
        self.display_image()


    def initialize_elements(self):
        self.explorer_button = tk.Button(self, text='BROWSE FILES',command=lambda: self.browse_files('./sudokus'), font=("Helvetica", 16), **self.button_setting)
        self.image_label = tk.Label(self, text='No Image Chosen', font=('Helvetica', 16), bg='#F9E4D4', fg='#9C0F48', border=0)
        self.solve_button = tk.Button(self, text='SOLVE SUDOKU', command=self.process_sudoku_image, font=('Helvetica', 16), **self.button_setting)

        self.canvas = tk.Canvas(self, width=775, height=775, bd=0, highlightthickness=0)


    def place_elements(self):
        self.explorer_button.grid(row=0, column=0, sticky=tk.NW)
        self.image_label.grid(row=0, column=1)
        self.solve_button.grid(row=0, column=2, sticky=tk.NE)

        self.canvas.grid(row=2, column=0, columnspan=3, pady=4, sticky=tk.NSEW)


    def browse_files(self, initial_directory):
        """
        Opens windows explorer to let user choose an image to load\n
        Supports [.jpg, .jpeg, .png]
        """
        filepath = filedialog.askopenfilename(
            initialdir=initial_directory,
            title='Select a Sudoku Image',
            filetypes=[('Image Files', '.jpg .jpeg .png')])

        self.chosen_image_path = filepath

        try:
            self.load_image(self.chosen_image_path)
        
        except AttributeError:
            return

        image_name = self.filename_from_path(filepath)
        self.image_label.configure(text=image_name)

        self.display_image()


    def filename_from_path(self, full_path):
        """
        Returns a file name with file extension from a full path name
        """
        full_path = full_path.split('/')
        path_depth = len(full_path)
        file_name = full_path[path_depth - 1]
        
        return file_name


    def load_image(self, image_path):
        """
        Loads an image from {image_path} into self.image and formats it to fit on canvas
        """
        self.image = Image.open(image_path)

        self.image = self.image.resize((775, 775), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(self.image)


    def display_image(self):
        """
        Displays {self.image} on canvas
        """
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)


    def process_sudoku_image(self):
        """
        Starting point in a procedure for solving sudoku from a loaded image.\n
        Process image >> Zoom in to sudoku >> Cut it in 81 piece each containg one field >> Image recognition >> Solve for missing fields (backtracking)
        """
        image_processor = ImageProcessor(self.chosen_image_path)

        # Saves zoomed in sudoku image to 'temp.jpg'
        image_processor.save_sudoku_image()

        # Loads and displays zoomed image to canvas
        self.load_image('./resources/temp.jpg')
        self.display_image()
        
        # Makes a list of images of each field in a sudoku image
        image_boxes = image_processor.split_number_boxes()

        # Solves sudoku and overlays solution
        self.after(100, self.solve_sudoku, image_boxes)


    def solve_sudoku(self, image_boxes):
        digit_classifier = DigitClassifier(image_boxes, './resources/lenet_digit_model.h5')

        # Get a list of lists of recognized digits (missing fields = 0)
        predicted_board = digit_classifier.sudoku_board()

        unsolved_board = deepcopy(predicted_board)

        # Solve for missing fields
        sudoku_solver = SudokuSolver(predicted_board)
        solved_board = sudoku_solver.board

        # Display solution over a loaded image
        self.digit_overlay(unsolved_board, solved_board)


    def display_number(self, x, y, digit_to_display):
        """
        Displays {digit_to_display} on self.canvas at coordinates {x, y}
        """
        self.canvas.create_text(x, y, font=('Helvetica', 50), text=f'{digit_to_display}', fill='#9C0F48')


    def digit_overlay(self, predicted_board, solved_board):
        """
        Creates an overlay of missing digits over an image on canvas
        """
        digit_spacing = 775 // 9
        counter = 1

        for i in range(9):
            x = digit_spacing // 2 + i * digit_spacing

            for j in range(9):
                y = digit_spacing // 2 + j * digit_spacing

                # Display a digit only on fields where one is missing
                if predicted_board[j][i] != 0:
                    continue

                digit = solved_board[j][i]
                counter += 1

                # Display each digit 50ms apart 
                self.after(counter * 50, self.display_number, x, y, digit)