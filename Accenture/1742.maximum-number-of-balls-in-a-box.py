#
# @lc app=leetcode id=1742 lang=python3
#
# [1742] Maximum Number of Balls in a Box
#
# https://leetcode.com/problems/maximum-number-of-balls-in-a-box/description/
#
# algorithms
# Easy (74.95%)
# Likes:    658
# Dislikes: 171
# Total Accepted:    88.1K
# Total Submissions: 118K
# Testcase Example:  "1"
#
# You are working in a ball factory where you have n balls numbered from
# lowLimit up to highLimit inclusive (i.e., n == highLimit - lowLimit + 1), and
# an infinite number of boxes numbered from 1 to infinity.
#
# Your job at this factory is to put each ball in the box with a number equal
# to the sum of digits of the ball's number. For example, the ball number 321
# will be put in the box number 3 + 2 + 1 = 6 and the ball number 10 will be
# put in the box number 1 + 0 = 1.
#
# Given two integers lowLimit and highLimit, return the number of balls in the
# box with the most balls.
#
# Example 1:
#
# Input: lowLimit = 1, highLimit = 10
# Output: 2
# Explanation:
# Box Number: 1 2 3 4 5 6 7 8 9 10 11 ...
# Ball Count: 2 1 1 1 1 1 1 1 1 0 0 ...
# Box 1 has the most number of balls with 2 balls.
#
# Example 2:
#
# Input: lowLimit = 5, highLimit = 15
# Output: 2
# Explanation:
# Box Number: 1 2 3 4 5 6 7 8 9 10 11 ...
# Ball Count: 1 1 1 1 2 2 1 1 1 0 0 ...
# Boxes 5 and 6 have the most number of balls with 2 balls in each.
#
# Example 3:
#
# Input: lowLimit = 19, highLimit = 28
# Output: 2
# Explanation:
# Box Number: 1 2 3 4 5 6 7 8 9 10 11 12 ...
# Ball Count: 0 1 1 1 1 1 1 1 1 2 0 0 ...
# Box 10 has the most number of balls with 2 balls.
#
# Constraints:
#
# 1 <= lowLimit <= highLimit <= 10^5
#

# @lc code=start
from collections import Counter


class Solution:
    def countBalls(self, lowLimit: int, highLimit: int) -> int:
        """
        Interview explanation:
        Place each ball x into box = digit-sum(x); return the fullest box size.

        Algorithm:
        - Count digit sums over [lowLimit, highLimit]; return max frequency.

        Complexity: O((high-low) * log high) time, O(1) space relative to range size of sums.
        """
        def digsum(x: int) -> int:
            s = 0
            while x:
                s += x % 10
                x //= 10
            return s

        cnt: Counter = Counter()
        for x in range(lowLimit, highLimit + 1):
            cnt[digsum(x)] += 1
        return max(cnt.values())
# @lc code=end
