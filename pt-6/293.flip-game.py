#
# @lc app=leetcode id=293 lang=python3
#
# [293] Flip Game
#
# https://leetcode.com/problems/flip-game/description/
#
# algorithms
# Easy (65.06%)
# Likes:    232
# Dislikes: 478
# Total Accepted:    79.8K
# Total Submissions: 122.7K
# Testcase Example:  "\"++++\""
#
#
# You are playing a Flip Game with your friend.
#
# You are given a string currentState that contains only '+' and '-'. You
# and your friend take turns to flip two consecutive "++" into "--". The
# game ends when a person can no longer make a move, and therefore the
# other person will be the winner.
#
# Return all possible states of the string currentState after one valid
# move. You may return the answer in any order. If there is no valid move,
# return an empty list [].
#
# Example 1:
#
# Input: currentState = "++++"
# Output: ["--++","+--+","++--"]
#
# Example 2:
#
# Input: currentState = "+"
# Output: []
#
# Constraints:
#
# 1 <= currentState.length <= 500
#
# currentState[i] is either '+' or '-'.
#
# @lc code=start
from typing import List


class Solution:
    def generatePossibleNextMoves(self, currentState: str) -> List[str]:
        """
        Interview explanation:
        A move flips any "++" substring to "--". Enumerate all starting indices
        where two consecutive '+' appear and produce the resulting states.

        Complexity: O(n^2) time/space to build all strings of length n.
        """
        res = []
        for i in range(len(currentState) - 1):
            if currentState[i] == "+" and currentState[i + 1] == "+":
                res.append(currentState[:i] + "--" + currentState[i + 2 :])
        return res
# @lc code=end

