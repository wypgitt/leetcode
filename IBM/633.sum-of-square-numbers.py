#
# @lc app=leetcode id=633 lang=python3
#
# [633] Sum of Square Numbers
#
# https://leetcode.com/problems/sum-of-square-numbers/description/
#
# algorithms
# Medium (36.97%)
# Likes:    3488
# Dislikes: 623
# Total Accepted:    462K
# Total Submissions: 1.3M
# Testcase Example:  "5"
#
# Given a non-negative integer c, decide whether there're two integers a and b
# such that a^2 + b^2 = c.
#
# Example 1:
#
# Input: c = 5
# Output: true
# Explanation: 1 * 1 + 2 * 2 = 5
#
# Example 2:
#
# Input: c = 3
# Output: false
#
# Constraints:
#
# 0 <= c <= 2^31 - 1
#

# @lc code=start

class Solution:
    def judgeSquareSum(self, c: int) -> bool:
        """
        Interview explanation:
        Decide if c = a^2 + b^2 for nonnegative integers a,b. Two pointers on
        [0, floor(sqrt(c))].

        Algorithm:
        - lo, hi = 0, int(sqrt(c)).
        - While lo <= hi: s = lo^2+hi^2; move lo/hi by comparison to c.

        Complexity: O(sqrt(c)) time, O(1) space.
        """
        lo, hi = 0, int(c**0.5)
        while lo <= hi:
            s = lo * lo + hi * hi
            if s == c:
                return True
            if s < c:
                lo += 1
            else:
                hi -= 1
        return False
# @lc code=end
