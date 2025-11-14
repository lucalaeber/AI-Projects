from Field import Field


class Sudoku:

    def __init__(self, filename):
        self.board = self.read_sudoku(filename)

    def __str__(self):
        output = "╔═══════╦═══════╦═══════╗\n"
        # iterate through rows
        for i in range(9):
            if i == 3 or i == 6:
                output += "╠═══════╬═══════╬═══════╣\n"
            output += "║ "
            # iterate through columns
            for j in range(9):
                if j == 3 or j == 6:
                    output += "║ "
                output += str(self.board[i][j]) + " "
            output += "║\n"
        output += "╚═══════╩═══════╩═══════╝\n"
        return output

    @staticmethod
    def read_sudoku(filename):
        """
        Read in a sudoku file
        @param filename: Sudoku filename
        @return: A 9x9 grid of Fields where each field is initialized with all its neighbor fields
        """
        assert filename is not None and filename != "", "Invalid filename"
        # Setup 9x9 grid
        grid = [[Field for _ in range(9)] for _ in range(9)]

        try:
            with open(filename, "r") as file:
                for row, line in enumerate(file):
                    for col_index, char in enumerate(line):
                        if char == '\n':
                            continue
                        if int(char) == 0:
                            grid[row][col_index] = Field()
                        else:
                            grid[row][col_index] = Field(int(char))

        except FileNotFoundError:
            print("Error opening file: " + filename)

        Sudoku.add_neighbours(grid)
        return grid

    @staticmethod
    def add_neighbours(grid):
        """
        Adds a list of neighbors to each field
        @param grid: 9x9 list of Fields
        
        IDEA:
            1. For every row, colum adn block, creating a set (since it cant contain duplicates) with all the neighbors.
            2. Setting the neighbors using set_neighbours as the set converted into a list.
            
            
            Are we storing neighbours right? --> Storing strings name but not the field it represents??
            
            
        """

        for row in range(9):
            for col in range(9):
                neighbors = set()
                
                # Add the variables in the row
                for col_vars in range(9):
                    if col_vars != col:
                        neighbors.add(f"X{row}{col_vars}")
                
                # Add the variables in the column
                for row_vars in range(9):
                    if row_vars != row:
                        neighbors.add(f"X{row_vars}{col}")
                
                # Add the variables in the 3x3 subgrid
                block_row_start = (row // 3) * 3
                block_col_start = (col // 3) * 3
                for row_vars in range(block_row_start, block_row_start + 3):
                    for col_vars in range(block_col_start, block_col_start + 3):
                        if (row_vars != row or col_vars != col):
                            neighbors.add(f"X{row_vars}{col_vars}") 
                
                # Assign neighbors in variable format
                grid[row][col].set_neighbours(list(neighbors))

    def board_to_string(self):

        output = ""
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                output += self.board[row][col].get_value()
            output += "\n"
        return output

    def get_board(self):
        return self.board
