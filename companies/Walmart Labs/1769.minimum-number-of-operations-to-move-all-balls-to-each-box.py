#
# @lc app=leetcode id=1769 lang=python3
#
# [1769] Minimum Number of Operations to Move All Balls to Each Box
#
# https://leetcode.com/problems/minimum-number-of-operations-to-move-all-balls-to-each-box/description/
#
# algorithms
# Medium (90.13%)
# Likes:    3152
# Dislikes: 140
# Total Accepted:    347K
# Total Submissions: 384K
# Testcase Example:  "\"110\""
#
# You have n boxes. You are given a binary string boxes of length n, where
# boxes[i] is '0' if the i^th box is empty, and '1' if it contains one ball.
#
# In one operation, you can move one ball from a box to an adjacent box. Box i
# is adjacent to box j if abs(i - j) == 1. Note that after doing so, there may
# be more than one ball in some boxes.
#
# Return an array answer of size n, where answer[i] is the minimum number of
# operations needed to move all the balls to the i^th box.
#
# Each answer[i] is calculated considering the initial state of the boxes.
#
# Example 1:
#
# Input: boxes = "110"
# Output: [1,1,3]
# Explanation: The answer for each box is as follows:
# 1) First box: you will have to move one ball from the second box to the first
# box in one operation.
# 2) Second box: you will have to move one ball from the first box to the
# second box in one operation.
# 3) Third box: you will have to move one ball from the first box to the third
# box in two operations, and move one ball from the second box to the third box
# in one operation.
#
# Example 2:
#
# Input: boxes = "001011"
# Output: [11,8,5,4,3,4]
#
# Constraints:
#
# n == boxes.length
#
# 1 <= n <= 2000
#
# boxes[i] is either '0' or '1'.
#

# @lc code=start
from typing import List


class Solution:
    def minOperations(self, boxes: str) -> List[int]:
        """
        Interview explanation:
        For each box i, sum |j-i| over balls at j. Two-pass: left→right accumulate
        cost moving balls from the left; right→left similarly; add both.

        Algorithm:
        - left pass: balls/ops running; ans[i]+=ops; then update if ball at i.
        - right pass analogously.

        Complexity: O(n) time, O(n) space.
        """
        n = len(boxes)
        ans = [0] * n
        balls = ops = 0
        for i in range(n):
            ans[i] += ops
            balls += boxes[i] == "1"
            ops += balls
        balls = ops = 0
        for i in range(n - 1, -1, -1):
            ans[i] += ops
            balls += boxes[i] == "1"
            ops += balls
        return ans

    def minOperations_bruteforce(self, boxes: str) -> List[int]:
        """
        Interview explanation:
        Alternate O(n^2): for each target i, sum distances to every ball.

        Algorithm:
        - Collect ball indices; for each i sum abs(j-i).

        Complexity: O(n^2) time, O(n) space.
        """
        balls = [i for i, ch in enumerate(boxes) if ch == "1"]
        return [sum(abs(i - j) for j in balls) for i in range(len(boxes))]
# @lc code=end
