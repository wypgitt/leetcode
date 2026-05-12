#
# @lc app=leetcode id=1041 lang=python3
#
# [1041] Robot Bounded In Circle
#
# https://leetcode.com/problems/robot-bounded-in-circle/description/
#
# algorithms
# Medium (56.52%)
# Likes:    3865
# Dislikes: 718
# Total Accepted:    274.2K
# Total Submissions: 485.1K
# Testcase Example:  '"GGLLGG"'
#
# On an infinite plane, a robot initially stands at (0, 0) and faces north.
# Note that:
# 
# 
# The north direction is the positive direction of the y-axis.
# The south direction is the negative direction of the y-axis.
# The east direction is the positive direction of the x-axis.
# The west direction is the negative direction of the x-axis.
# 
# 
# The robot can receive one of three instructions:
# 
# 
# "G": go straight 1 unit.
# "L": turn 90 degrees to the left (i.e., anti-clockwise direction).
# "R": turn 90 degrees to the right (i.e., clockwise direction).
# 
# 
# The robot performs the instructions given in order, and repeats them
# forever.
# 
# Return true if and only if there exists a circle in the plane such that the
# robot never leaves the circle.
# 
# 
# Example 1:
# 
# 
# Input: instructions = "GGLLGG"
# Output: true
# Explanation: The robot is initially at (0, 0) facing the north direction.
# "G": move one step. Position: (0, 1). Direction: North.
# "G": move one step. Position: (0, 2). Direction: North.
# "L": turn 90 degrees anti-clockwise. Position: (0, 2). Direction: West.
# "L": turn 90 degrees anti-clockwise. Position: (0, 2). Direction: South.
# "G": move one step. Position: (0, 1). Direction: South.
# "G": move one step. Position: (0, 0). Direction: South.
# Repeating the instructions, the robot goes into the cycle: (0, 0) --> (0, 1)
# --> (0, 2) --> (0, 1) --> (0, 0).
# Based on that, we return true.
# 
# 
# Example 2:
# 
# 
# Input: instructions = "GG"
# Output: false
# Explanation: The robot is initially at (0, 0) facing the north direction.
# "G": move one step. Position: (0, 1). Direction: North.
# "G": move one step. Position: (0, 2). Direction: North.
# Repeating the instructions, keeps advancing in the north direction and does
# not go into cycles.
# Based on that, we return false.
# 
# 
# Example 3:
# 
# 
# Input: instructions = "GL"
# Output: true
# Explanation: The robot is initially at (0, 0) facing the north direction.
# "G": move one step. Position: (0, 1). Direction: North.
# "L": turn 90 degrees anti-clockwise. Position: (0, 1). Direction: West.
# "G": move one step. Position: (-1, 1). Direction: West.
# "L": turn 90 degrees anti-clockwise. Position: (-1, 1). Direction: South.
# "G": move one step. Position: (-1, 0). Direction: South.
# "L": turn 90 degrees anti-clockwise. Position: (-1, 0). Direction: East.
# "G": move one step. Position: (0, 0). Direction: East.
# "L": turn 90 degrees anti-clockwise. Position: (0, 0). Direction: North.
# Repeating the instructions, the robot goes into the cycle: (0, 0) --> (0, 1)
# --> (-1, 1) --> (-1, 0) --> (0, 0).
# Based on that, we return true.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= instructions.length <= 100
# instructions[i] is 'G', 'L' or, 'R'.
# 
# 
#

# @lc code=start
class Solution:
    def isRobotBounded(self, instructions: str) -> bool:
        x = y = 0
        direction = 0
        moves = ((0, 1), (1, 0), (0, -1), (-1, 0))

        for instruction in instructions:
            if instruction == "G":
                dx, dy = moves[direction]
                x += dx
                y += dy
            elif instruction == "L":
                direction = (direction - 1) % 4
            else:
                direction = (direction + 1) % 4

        return (x, y) == (0, 0) or direction != 0
# @lc code=end

"""
Interview Explanation

Core idea:
It is enough to simulate the instruction string once. After one cycle, the
robot is bounded if it is back at the origin, or if it is facing a different
direction. A changed direction means repeated cycles rotate its displacement
and eventually close a loop within four cycles.

Algorithm:
1. Represent directions as North, East, South, West with indices 0..3.
2. Simulate every instruction once.
3. Move on G; rotate the direction index on L/R.
4. Return True if position is origin or final direction is not North.

Data structure choice:
A tuple of four direction vectors gives O(1) movement and clean modular
rotation.

Correctness:
If the robot returns to the origin after one instruction cycle, repeating the
cycle never escapes. If it does not return but faces a new direction, the same
relative movement will be rotated on later cycles, and after at most four
cycles the net displacement cancels. If it does not return and still faces
North, every cycle adds the same displacement, so it moves unboundedly.

Complexity:
Time is O(n), where n is the instruction length. Space is O(1).

Tests and edge cases:
- "GG" returns False because displacement repeats northward.
- "GL" returns True because direction changes.
- "GGRRGG" returns True because it returns to origin.
- Strings with only turns are bounded at the origin.
"""
