#
# @lc app=leetcode id=353 lang=python3
#
# [353] Design Snake Game
#
# https://leetcode.com/problems/design-snake-game/description/
#
# algorithms
# Medium (40.07%)
# Likes:    1018
# Dislikes: 353
# Total Accepted:    107.2K
# Total Submissions: 267.5K
# Testcase Example:  "[\"SnakeGame\",\"move\",\"move\",\"move\",\"move\",\"move\",\"move\"]\n[[3,2,[[1,2],[0,1]]],[\"R\"],[\"D\"],[\"R\"],[\"U\"],[\"L\"],[\"U\"]]"
#
#
# Design a Snake game that is played on a device with screen size height x
# width. Play the game online if you are not familiar with the game.
#
# The snake is initially positioned at the top left corner (0, 0) with a
# length of 1 unit.
#
# You are given an array food where food[i] = (r_i, c_i) is the row and
# column position of a piece of food that the snake can eat. When a snake
# eats a piece of food, its length and the game's score both increase by
# 1.
#
# Each piece of food appears one by one on the screen, meaning the second
# piece of food will not appear until the snake eats the first piece of
# food.
#
# When a piece of food appears on the screen, it is guaranteed that it
# will not appear on a block occupied by the snake.
#
# The game is over if the snake goes out of bounds (hits a wall) or if its
# head occupies a space that its body occupies after moving (i.e. a snake
# of length 4 cannot run into itself).
#
# Implement the SnakeGame class:
#
# SnakeGame(int width, int height, int[][] food) Initializes the object
# with a screen of size height x width and the positions of the food.
#
# int move(String direction) Returns the score of the game after applying
# one direction move by the snake. If the game is over, return -1.
#
# Example 1:
#
# Input
# ["SnakeGame", "move", "move", "move", "move", "move", "move"]
# [[3, 2, [[1, 2], [0, 1]]], ["R"], ["D"], ["R"], ["U"], ["L"], ["U"]]
# Output
# [null, 0, 0, 1, 1, 2, -1]
#
# Explanation
# SnakeGame snakeGame = new SnakeGame(3, 2, [[1, 2], [0, 1]]);
# snakeGame.move("R"); // return 0
# snakeGame.move("D"); // return 0
# snakeGame.move("R"); // return 1, snake eats the first piece of food.
# The second piece of food appears at (0, 1).
# snakeGame.move("U"); // return 1
# snakeGame.move("L"); // return 2, snake eats the second food. No more
# food appears.
# snakeGame.move("U"); // return -1, game over because snake collides with
# border
#
# Constraints:
#
# 1 <= width, height <= 10^4
#
# 1 <= food.length <= 50
#
# food[i].length == 2
#
# 0 <= r_i < height
#
# 0 <= c_i < width
#
# direction.length == 1
#
# direction is 'U', 'D', 'L', or 'R'.
#
# At most 10^4 calls will be made to move.
#
# @lc code=start
from collections import deque
from typing import List, Set, Tuple


class SnakeGame:
    """
    Interview explanation:
    Deque stores snake body (head at right); set for O(1) body occupancy.
    Move: compute new head; die on wall/body (except tail about to leave);
    eat food then grow else popleft tail.

    Algorithm:
    - __init__: width, height, food list, score, deque([(0,0)]), set.
    - move(dir): new head; if invalid return -1; if food, score++ and advance
      food index (no pop); else popleft; append head; return score.

    Complexity: O(1) per move amortized, O(food + snake) space.
    """

    def __init__(self, width: int, height: int, food: List[List[int]]):
        """
        Interview explanation:
        Snake starts at (0,0). Body is a deque (head at right) plus a set for
        O(1) collision checks; food is consumed in order.

        Algorithm:
        - Store board size, food list/index, score, body deque, occupied set, dirs.

        Complexity: O(1) init beyond storing food, O(food + snake) space.
        """
        self.w = width
        self.h = height
        self.food = food
        self.fi = 0
        self.score = 0
        self.body: deque[Tuple[int, int]] = deque([(0, 0)])
        self.occupied: Set[Tuple[int, int]] = {(0, 0)}
        self.dirs = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}

    def move(self, direction: str) -> int:
        """
        Interview explanation:
        Advance head; die on wall/self (tail may leave first if not growing);
        eat food to grow, else pop the tail.

        Algorithm:
        - new head = old head + dir; if out of bounds return -1.
        - If not food: popleft tail from body/occupied.
        - If new head in occupied return -1; else append; on food bump score/fi.

        Complexity: O(1) amortized time, O(1) extra space.
        """
        dr, dc = self.dirs[direction]
        r, c = self.body[-1]
        nr, nc = r + dr, c + dc
        if not (0 <= nr < self.h and 0 <= nc < self.w):
            return -1

        grow = (
            self.fi < len(self.food)
            and self.food[self.fi][0] == nr
            and self.food[self.fi][1] == nc
        )
        if not grow:
            tr, tc = self.body.popleft()
            self.occupied.remove((tr, tc))

        if (nr, nc) in self.occupied:
            return -1

        self.body.append((nr, nc))
        self.occupied.add((nr, nc))
        if grow:
            self.fi += 1
            self.score += 1
        return self.score


# Your SnakeGame object will be instantiated and called as such:
# obj = SnakeGame(width, height, food)
# param_1 = obj.move(direction)
# @lc code=end
