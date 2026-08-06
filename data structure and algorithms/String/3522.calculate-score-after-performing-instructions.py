#
# @lc app=leetcode id=3522 lang=python3
#
# [3522] Calculate Score After Performing Instructions
#
# https://leetcode.com/problems/calculate-score-after-performing-instructions/description/
#
# algorithms
# Medium (57.31%)
# Likes:    48
# Dislikes: 10
# Total Accepted:    41.6K
# Total Submissions: 72.5K
# Testcase Example:  "[\"jump\",\"add\",\"add\",\"jump\",\"add\",\"jump\"]\n[2,1,3,1,-2,-3]"
#
#
# You are given two arrays, instructions and values, both of size n.
#
# You need to simulate a process based on the following rules:
#
# You start at the first instruction at index i = 0 with an initial score
# of 0.
#
# If instructions[i] is "add":
#
# Add values[i] to your score.
#
# Move to the next instruction (i + 1).
#
# If instructions[i] is "jump":
#
# Move to the instruction at index (i + values[i]) without modifying your
# score.
#
# The process ends when you either:
#
# Go out of bounds (i.e., i < 0 or i >= n), or
#
# Attempt to revisit an instruction that has been previously executed. The
# revisited instruction is not executed.
#
# Return your score at the end of the process.
#
# Example 1:
#
# Input: instructions = ["jump","add","add","jump","add","jump"], values =
# [2,1,3,1,-2,-3]
#
# Output: 1
#
# Explanation:
#
# Simulate the process starting at instruction 0:
#
# At index 0: Instruction is "jump", move to index 0 + 2 = 2.
#
# At index 2: Instruction is "add", add values[2] = 3 to your score and
# move to index 3. Your score becomes 3.
#
# At index 3: Instruction is "jump", move to index 3 + 1 = 4.
#
# At index 4: Instruction is "add", add values[4] = -2 to your score and
# move to index 5. Your score becomes 1.
#
# At index 5: Instruction is "jump", move to index 5 + (-3) = 2.
#
# At index 2: Already visited. The process ends.
#
# Example 2:
#
# Input: instructions = ["jump","add","add"], values = [3,1,1]
#
# Output: 0
#
# Explanation:
#
# Simulate the process starting at instruction 0:
#
# At index 0: Instruction is "jump", move to index 0 + 3 = 3.
#
# At index 3: Out of bounds. The process ends.
#
# Example 3:
#
# Input: instructions = ["jump"], values = [0]
#
# Output: 0
#
# Explanation:
#
# Simulate the process starting at instruction 0:
#
# At index 0: Instruction is "jump", move to index 0 + 0 = 0.
#
# At index 0: Already visited. The process ends.
#
# Constraints:
#
# n == instructions.length == values.length
#
# 1 <= n <= 10^5
#
# instructions[i] is either "add" or "jump".
#
# -10^5 <= values[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def calculateScore(self, instructions: List[str], values: List[int]) -> int:
        """
        Interview explanation:
        Simulate from index 0: add updates score and steps +1; jump only moves.
        Stop on out-of-bounds or revisiting a prior index.

        Algorithm:
        - Track visited array; while i in range and not visited: mark, then add or jump.
        - Return accumulated score.

        Complexity: O(n) time, O(n) space.
        """
        n = len(instructions)
        visited = [False] * n
        score = 0
        i = 0
        while 0 <= i < n and not visited[i]:
            visited[i] = True
            if instructions[i] == "add":
                score += values[i]
                i += 1
            else:
                i += values[i]
        return score

    def calculateScore_set(self, instructions: List[str], values: List[int]) -> int:
        """
        Interview explanation:
        Alternate: same simulation with a hash set for visited indices.

        Algorithm:
        - Identical control flow; store seen indices in a set.

        Complexity: O(n) time, O(n) space.
        """
        n = len(instructions)
        seen = set()
        score = 0
        i = 0
        while 0 <= i < n and i not in seen:
            seen.add(i)
            if instructions[i] == "add":
                score += values[i]
                i += 1
            else:
                i += values[i]
        return score
# @lc code=end
