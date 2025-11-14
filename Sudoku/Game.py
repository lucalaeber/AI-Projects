import time
class Game:

    def __init__(self, sudoku):
        self.sudoku = sudoku

    def show_sudoku(self):
        print(self.sudoku)
        
        
        
    # HEURISTIC MPLEMENTATION
    def minimum_remaining_values(self, queue, D):
        """
        IDEA:
            Choosing the variable with the fewest legal values in the domain.
            Sorting the queueu based on the domain of the first varible in the arc.
        
        """
        sorted_queue = list(sorted(queue, key = lambda arc : len(D[arc[0]])))
        return sorted_queue
    
    def degree_heuristic(self, queue, D):
        """
        IDEA:
            It is applied when the are variables with the same MRV.
        
        """
        degree_count = {}
        for arc in queue:
            var = arc[0]
            degree_count[var] = degree_count.get(var, 0) + 1
        
        degree_sorted_queue = list(sorted(queue, key = lambda arc : degree_count[arc[0]], reverse = True))
        return degree_sorted_queue
   
    def prioritize_finalized_arcs(self, queue, D):
        """
        IDEA:
            Prioritizing arcs whose second variable is finalized.
        
        """
        finalized_sort = list(sorted(queue, key = lambda arc : len(D[arc[1]]) == 1, reverse = True))
        return finalized_sort
    
    def apply_heuristic(self, queue, D, heuristic = "mrv degree finalized"): # change here to change heuristic
        if heuristic == "default":
            return queue  
        
        elif heuristic == "mrv":
            return self.minimum_remaining_values(queue, D)
        
        elif heuristic == "degree":
            return self.degree_heuristic(queue, D)
        
        elif heuristic == "finalized":
            return self.prioritize_finalized_arcs(queue, D)
        
        elif heuristic == "mrv degree":
            mrv_queue = self.minimum_remaining_values(queue, D)
            return self.degree_heuristic(mrv_queue, D)
        
        elif heuristic == "mrv finalized":
            mrv_queue = self.minimum_remaining_values(queue, D)
            return self.prioritize_finalized_arcs(mrv_queue, D)
        
        elif heuristic == "degree finalized":
            degree_queue = self.degree_heuristic(queue, D)
            return self.prioritize_finalized_arcs(degree_queue, D)
        
        elif heuristic == "mrv degree finalized":
            mrv_queue = self.minimum_remaining_values(queue, D)
            mrv_degree_queue = self.degree_heuristic(mrv_queue, D)
            return self.prioritize_finalized_arcs(mrv_degree_queue, D)
        else:
            raise ValueError(f"Unknown heuristic: {heuristic}")
        
    #Other code:
    
    def solve(self) -> bool:
        """
        Implementation of the AC-3 algorithm
        @return: true if the constraints can be satisfied, false otherwise
        """
        
        """
        IDEA:
            1. A function to convert the initial state of the sudoku into a CSP problem, by obtaining the variables (each grid), 
            mapping their corresponding domain (values it can take: if finished: domain is the value, if not finished: domain 1-9),
            and construct the constraints of all different for rows, columns and blocks.
            
            2. Constructing arcs (between 2 vars) by accessing the previously created contraints, where for every constraint, 
            accessing the constraint variables. 
                If the varaible is finalized we create an arc to all non finalized variables.
                else we craete arcs to all variables in the constarint.
                
            3. Iteratively take the first arc (Xa, Xb)in the queue/list of all arcs and if there is a conflicting value in the domain 
            of the variable Xb we remove it from the domain of Xa. Once the domain of Xa comes to a single value assign the value to 
            the corresponding grid. 
            
                !!!! Not sure??? -> It will always show a solution if if wrong? No solution should be no arcs and variables with no 
                value remaining. 
                
                3.1 conditions: if D of Xa = 0, return false
                                if D of Xa changed add (Xk, Xa) where k is neighbor of Xa - Xb
            
            4. Once all arcs are satisfied and all varaibles have a value, return true.
            
        
        """
        
        # STEP 1: converting sudoku into CSP
        def sudoku_to_CSP(sudoku):
            
            # Variables and their domains
            Vars = []
            Dom = {} #Dict to map vars to their domains -> Key: variable, Value: domain list of values
            
            # Constraints
            Cons = []
            
            # Filling in variables and domains
            for row in range(9):
                for col in range(9):
                    #Name each of the grids (X00, X01, etc.)
                    var = f"X{row}{col}"
                    Vars.append(var)
                    
                    if sudoku.board[row][col].is_finalized():
                        Dom[var] = [sudoku.board[row][col].get_value()] #if the variable alrady has a value, get each value and assign it to the domain
                    else:
                        Dom[var] = list(range(1, 10)) #If it is an empty grid, domain is 1-9
            
            # Adding the constraints for each row (all must be different)
            for row in range(9):
                row_vars = []
                for col in range(9):
                    row_vars.append(f"X{row}{col}")
                Cons.append((row_vars, "all_different")) 
                
            # Adding constraints for the columns (all different)
            for col in range(9):
                col_vars = []
                for row in range(9):
                    col_vars.append(f"X{row}{col}")
                Cons.append((col_vars, "all_different"))

            
            # Adding the constraints for the 3x3 blocks (all different)
            for row in range(3):
                for col in range(3):
                    box_vars = []
                    for i in range(3):
                        for j in range(3):
                            var = f"X{3 * row + i}{3 * col + j}"
                            box_vars.append(var)
                    Cons.append((box_vars, "all_different"))
            
            return (Vars, Dom, Cons) # returning the triplet CSP form of the sudoku

        

        # STEP 2: creating arcs between variables
        def create_arcs():
            
            V, D, C = sudoku_to_CSP(self.sudoku) #Triplet of the CSP
        
            # List of all arcs, where each arc is a tuple of 2 variaables
            arcs = []
            
            #Iterate over the variables of each constraint
            for constraint in C:
                for var in constraint[0]:
                    if len(D[var]) > 1:
                        for xvar in constraint[0]:
                            arc = (var, xvar)
                            if xvar!=var and arc not in arcs:
                                arcs.append(arc)
            return arcs, V, D, C
        
         
            
        #STEP 3: Iteratively take the frist arc in the queue and check for conflicting variables y the domains of the variables 
        start_time = time.time()
        
        queue, V, D, C = create_arcs()
        heuristic_queue = self.apply_heuristic(queue, D, heuristic = "mrv degree finalized") # change here to change heuristic
        num_arcs = 0  #complexity for nº arcs
        
        while True:
            if len(heuristic_queue) == 0:
                break
            
            arc = heuristic_queue.pop(0) #take the frist arc in the queue
            num_arcs +=1
            
            # Take for variables in the arc
            X = arc[0] 
            Y = arc[1]
            # Coordinats of both variables (row, column)
            Xr = int(X[1])
            Xc = int(X[2])
            
            # Domains of both variables
            Xd = D[X]
            Yd = D[Y]
            # If the length of the second varible, in short remove it from the domain of the first variable
            if len(Yd) == 1:
                value = Yd[0]
                if value in Xd:
                    Xd.remove(value)
                    #If once removed conflicting values, the domain of the first varible is 1 value, assign that value to the variable
                    if len(Xd) == 1:
                        self.sudoku.board[Xr][Xc].set_value(Xd[0])
                        
                    if len(Xd) == 0: #if the domain of the first varible ends up empty, return false since its unsolvable
                        return False
                    D[X] = Xd
                    
                    #Getting the neighbors and adding the into arcs for the queue
                    neighbours = self.sudoku.board[Xr][Xc].get_other_neighbours(Y)
                    
                    for neighbour in neighbours:
                        if len(D[neighbour]) > 1:
                            arc = (neighbour, X)
                            if arc not in heuristic_queue:
                                heuristic_queue.append(arc)
            
                    heuristic_queue = self.apply_heuristic(heuristic_queue, D,"mrv degree finalized") # change here to change heuristic
        
        #print(queue) #debug
        end_time = time.time()          
        time_taken = end_time - start_time    #Complexity for time
        
        #Showing result of sudoku
        self.show_sudoku()
        
        print(f"Number of arcs used: {num_arcs}")
        print(f"Time taken: {round(time_taken, 3)}s")
        
        return True




    def valid_solution(self) -> bool:
        """
        Checks the validity of a sudoku solution
        @return: true if the sudoku solution is correct
        """
        
        """
        Complexity:
            Runtime, nº of arcs evaluated, etc. 
            
        Validation:
            Checking each column, row and block have numbers ranging 1-9 no duplicates.
            
        """
        # TODO: implement valid_solution function
        
        # Goal for all rows, columns and blocks in the sudoku board
        goal = list(range(1, 10))
        board_state = self.sudoku.get_board()  # Get the board state 

        # Checking rows to goal
        for row in range(9):
            values = [board_state[row][col].get_value() for col in range(9)]
            if not sorted(values) == goal:
                return False
    
        # Checking columns to goal
        for col in range(9):
            values = [board_state[row][col].get_value() for row in range(9)]
            if not sorted(values) == goal:
                return False
    
        # Checking 3x3 subgrids to goal
        for box_row in range(3):
            for box_col in range(3):
                values = []
                # Moving through the different 3x3 boxes in the board:
                for row in range(box_row * 3, box_row * 3 + 3):
                    for col in range(box_col * 3, box_col * 3 + 3):
                        values.append(board_state[row][col].get_value())
                if not sorted(values) == goal:
                    return False

        return True

    
    
