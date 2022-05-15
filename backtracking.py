class SudokuSolver(object):
    def __init__(self, board):
        self.board = board
        self.height = len(self.board)
        self.width = len(self.board[0])
        self.backtrack()


    def __str__(self):
        ret_str = ""
        for i in range(self.height):
            for j in range(self.width):
                ret_str += f"{self.board[i][j]} "
            ret_str += "\n"
        return ret_str


    def backtrack(self):
        """
        Backtracking algorithm.\n
        Solves sudoku
        """
        empty_field_position = self.find_empty_field()

        if not empty_field_position:
            return True

        for i in range(1, self.width + 1):
            if self.validate(i, (empty_field_position)):
                self.board[empty_field_position[0]][empty_field_position[1]] = i

                if self.backtrack():
                    return True

                self.board[empty_field_position[0]][empty_field_position[1]] = 0

        return False


    def find_empty_field(self):
        """
        Finds field in {self.board} containing '0'
        """
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j] == 0:
                    return (i, j)

        return None


    def validate(self, number, position):
        """
        Runs a list of conditions to determine validity of {number}\n
        placement at {position}
        """
        conditions = [
            self.__check_row(number, position),
            self.__check_column(number, position),
            self.__check_square(number, position)
            ]

        return all(conditions)

    
    def __check_row(self, number, position):
        for i in range(self.width):
            if self.board[position[0]][i] == number and position[1] != i:
                return False
        return True


    def __check_column(self, number, position):
        for i in range(self.height):
            if self.board[i][position[1]] == number and position[0] != i:
                return False
        return True


    def __check_square(self, number, position):
        square_y = (position[0] // 3) * 3
        square_x = (position[1] // 3) * 3

        for i in range(square_y, square_y + 3):
            for j in range( square_x, square_x + 3):
                if self.board[i][j] == number and (i, j) != position:
                    return False

        return True

