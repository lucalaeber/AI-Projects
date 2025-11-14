from __future__ import annotations
from abc import abstractmethod
import numpy as np
from typing import TYPE_CHECKING
import time
if TYPE_CHECKING:
    from heuristics import Heuristic
    from board import Board
#import psutil
#import os
import tracemalloc

class PlayerController:
    """Abstract class defining a player
    """
    def __init__(self, player_id: int, game_n: int, heuristic: Heuristic) -> None:
        """
        Args:
            player_id (int): id of a player, can take values 1 or 2 (0 = empty)
            game_n (int): n in a row required to win
            heuristic (Heuristic): heuristic used by the player
        """
        self.player_id = player_id
        self.game_n = game_n
        self.heuristic = heuristic


    def get_eval_count(self) -> int:
        """
        Returns:
            int: The amount of times the heuristic was used to evaluate a board state
        """
        return self.heuristic.eval_count
    

    def __str__(self) -> str:
        """
        Returns:
            str: representation for representing the player on the board
        """
        if self.player_id == 1:
            return 'X'
        return 'O'
        

    @abstractmethod
    def make_move(self, board: Board) -> int:
        """Gets the column for the player to play in

        Args:
            board (Board): the current board

        Returns:
            int: column to play in
        """
        pass
class Tree:
    def __init__(self, root):
        self.root = root

class Node:
    def __init__(self, board, player, move = None, parent = None):
        self.board = board
        self.player = player
        self.move = move
        self.children_nodes = []
        self.parent = parent
        self.evaluation = None
        
    def generate_node(self, depth, max_depth = 5):
        valid_moves = []
        if depth >= max_depth:
            return
        for i in range(self.board.width):
            if self.board.is_valid(i):
                valid_moves.append(i)
        for move in valid_moves:
            new_board = self.board.get_new_board(move, self.player)
            new_player = 3 - self.player
            child_node = Node(new_board, new_player, move = move, parent = self)
            self.children_nodes.append(child_node)
            child_node.generate_node(depth + 1, max_depth)
            
    
class MinMaxPlayer(PlayerController):
    """Class for the minmax player using the minmax algorithm
    Inherits from Playercontroller
    """
    def __init__(self, player_id: int, game_n: int, depth: int, heuristic: Heuristic) -> None:
        """
        Args:
            player_id (int): id of a player, can take values 1 or 2 (0 = empty)
            game_n (int): n in a row required to win
            depth (int): the max search depth
            heuristic (Heuristic): heuristic used by the player
        """
        super().__init__(player_id, game_n, heuristic)
        self.depth: int = depth
        self.node_count = 0  # Count how many nodes are evaluated

    """
    def memory_usage(self):
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        return memory_info.rss # Returns memory usage in Bytes
    """

    def make_move(self, board: Board) -> int:
        """
        Gets the column for the player to play in

        Args:
            board (Board): the current board

        Returns:
            int: column to play in
        """
        # Makes the best move using the Minimax algorithm.
        self.node_count = 0  # Reset before each move
        total_memory_used = 0  # Initialize total memory used
        # Start tracemalloc for memory tracking
        tracemalloc.start()
        #start_memory = self.memory_usage()
        start_time = time.time()  # Start the timer
        best_move = self.minimax(Node(board, self.player_id), self.depth, True)[0]
        end_time = time.time() # End the timer
        #end_memory = self.memory_usage()
        current, peak = tracemalloc.get_traced_memory()  # Get memory usage
        total_memory_used += peak  # Add peak memory used for this move to total
        tracemalloc.stop()  # Stop tracemalloc
        print(f"Minimax evaluated {self.node_count} nodes in {end_time - start_time} seconds")
        #print(f"Memory used: {round(end_memory - start_memory, 5)} Bytes")
        print(f"Memory usage of MinMax: {current / 1024:.2f} KB")
        print(f"Total memory used: {total_memory_used / 1024:.2f} KB")
        print ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        return best_move
    
    def minimax(self, node: Node, depth: int, is_maximizing: bool):
        
        self.node_count += 1  # Increment for each node
        
        # Check for terminal node (win/loss or max depth reached)
        if depth == 0 or node.board.is_winning(self.game_n):  # Lowercase board attribute
            evaluation = self.heuristic.evaluate_board(self.player_id, node.board)
            return None, evaluation  # No specific move at terminal, just return evaluation score
    
        if is_maximizing:
            best_score = -np.inf
            best_move = None
            # Loop through all valid moves
            for move in range(node.board.width):
                if node.board.is_valid(move):
                    # Simulate the move by creating a new board state
                    new_board = node.board.get_new_board(move, self.player_id)
                    # Recursively call minimax for the opponent
                    _, score = self.minimax(Node(new_board, self.player_id), depth - 1, False)  # Pass a new Node
                    # Track the best score and the associated move
                    if score > best_score:
                        best_score = score
                        best_move = move
            return best_move, best_score
    
        else:
            opponent_id = 3 - self.player_id  # Assuming player_id is either 1 or 2
            best_score = np.inf
            best_move = None
            # Loop through all valid moves
            for move in range(node.board.width):
                if node.board.is_valid(move):
                    # Simulate the opponent's move by creating a new board state
                    new_board = node.board.get_new_board(move, opponent_id)
                    # Recursively call minimax for the player's turn
                    _, score = self.minimax(Node(new_board, opponent_id), depth - 1, True)  # Pass a new Node
                    # Track the best (lowest) score and the associated move
                    if score < best_score:
                        best_score = score
                        best_move = move
            return best_move, best_score
    
    """
    # Example:
    max_value: float = -np.inf # negative infinity
    max_move: int = 0
    for col in range(board.width):
        if board.is_valid(col):
            new_board: Board = board.get_new_board(col, self.player_id)
            value: int = self.heuristic.evaluate_board(self.player_id, new_board)
            if value > max_value:
                max_move = col

    # This returns the same as
    self.heuristic.get_best_action(self.player_id, board) # Very useful helper function!

    # This is obviously not enough (this is depth 1)
    # Your assignment is to create a data structure (tree) to store the gameboards such that you can evaluate a higher depths.
    # Then, use the minmax algorithm to search through this tree to find the best move/action to take!
    return max_move
    """


class AlphaBetaPlayer(PlayerController):
    """Class for the minmax player using the minmax algorithm with alpha-beta pruning
    Inherits from Playercontroller
    """
    def __init__(self, player_id: int, game_n: int, depth: int, heuristic: Heuristic) -> None:
        """
        Args:
            player_id (int): id of a player, can take values 1 or 2 (0 = empty)
            game_n (int): n in a row required to win
            depth (int): the max search depth
            heuristic (Heuristic): heuristic used by the player
        """
        super().__init__(player_id, game_n, heuristic)
        self.depth: int = depth
        self.node_count = 0
        
    """ 
    def memory_usage(self):
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        return memory_info.rss # Returns memory usage in Bytes
    """
    
    def make_move(self, board: Board) -> int:
        """Gets the column for the player to play in

        Args:
            board (Board): the current board

        Returns:
            int: column to play in
        """
        self.node_count = 0  # Reset before each move
        total_memory_used = 0  # Initialize total memory used
        start_time = time.time()  # Start the timer
        tracemalloc.start()
        #start_memory = self.memory_usage()
        best_move = self.alphabetaprune(Node(board, self.player_id), self.depth, -np.inf, np.inf, True)[0]
        end_time = time.time() # End the timer
        #end_memory = self.memory_usage()
        current, peak = tracemalloc.get_traced_memory()  # Get memory usage
        total_memory_used += peak  # Add peak memory used for this move to total
        tracemalloc.stop()  # Stop tracemalloc
        print(f'AlphaBeta evaluated {self.node_count} nodes in {end_time - start_time} seconds')
        #print(f"Memory used: {(end_memory - start_memory)} Bytes")
        print(f"Memory usage of AlphaBeta: {current / 1024:.2f} KB")
        print(f"Total memory used: {total_memory_used / 1024:.2f} KB")
        print ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        return best_move
    
    def alphabetaprune(self, node: Node, depth: int, alpha: float, beta: float, is_maximizing: bool):
        
        self.node_count += 1  # Increment for each node
        
        if depth == 0 or node.board.is_winning(self.game_n):  # Terminal node
            evaluation = self.heuristic.evaluate_board(self.player_id, node.board)
            return None, evaluation 
        

        if is_maximizing:
            best_score = -np.inf
            best_move = None

            for move in range(node.board.width):
                if node.board.is_valid(move):

                    new_board = node.board.get_new_board(move, self.player_id)
                    _, score = self.alphabetaprune(Node(new_board, self.player_id), depth - 1, alpha, beta, False)

                    if score > best_score:
                        best_score = score
                        best_move = move
                    alpha = max(alpha, best_score)
                    
                    if beta <= alpha:
                        break  
            return best_move, best_score

        else:  
            opponent_id = 3 - self.player_id 
            best_score = np.inf
            best_move = None

            for move in range(node.board.width):
                if node.board.is_valid(move):

                    new_board = node.board.get_new_board(move, opponent_id)
                    _, score = self.alphabetaprune(Node(new_board, opponent_id), depth - 1, alpha, beta, True)

                    if score < best_score:
                        best_score = score
                        best_move = move
                    beta = min(beta, best_score)

                    if beta <= alpha:
                        break
            return best_move, best_score


class HumanPlayer(PlayerController):
    """Class for the human player
    Inherits from Playercontroller
    """
    def __init__(self, player_id: int, game_n: int, heuristic: Heuristic) -> None:
        """
        Args:
            player_id (int): id of a player, can take values 1 or 2 (0 = empty)
            game_n (int): n in a row required to win
            heuristic (Heuristic): heuristic used by the player
        """
        super().__init__(player_id, game_n, heuristic)

    
    def make_move(self, board: Board) -> int:
        """Gets the column for the player to play in

        Args:
            board (Board): the current board

        Returns:
            int: column to play in
        """
        print(board)

        if self.heuristic is not None:
            print(f'Heuristic {self.heuristic} calculated the best move is:', end=' ')
            print(self.heuristic.get_best_action(self.player_id, board) + 1, end='\n\n')

        col: int = self.ask_input(board)

        print(f'Selected column: {col}')
        return col - 1
    

    def ask_input(self, board: Board) -> int:
        """Gets the input from the user

        Args:
            board (Board): the current board

        Returns:
            int: column to play in
        """
        try:
            col: int = int(input(f'Player {self}\nWhich column would you like to play in?\n'))
            assert 0 < col <= board.width
            assert board.is_valid(col - 1)
            return col
        except ValueError: # If the input can't be converted to an integer
            print('Please enter a number that corresponds to a column.', end='\n\n')
            return self.ask_input(board)
        except AssertionError: # If the input matches a full or non-existing column
            print('Please enter a valid column.\nThis column is either full or doesn\'t exist!', end='\n\n')
            return self.ask_input(board)
        