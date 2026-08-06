#
# @lc app=leetcode id=3783 lang=python3
#
# [3783] Mirror Distance of an Integer
#
# https://leetcode.com/problems/mirror-distance-of-an-integer/description/
#
# algorithms
# Easy (91.44%)
# Likes:    250
# Dislikes: 10
# Total Accepted:    181.5K
# Total Submissions: 198.5K
# Testcase Example:  "25"
#
#
# You are given an integer n.
#
# Define its mirror distance as: abs(n - reverse(n))​​​​​​​ where
# reverse(n) is the integer formed by reversing the digits of n.
#
# Return an integer denoting the mirror distance of n​​​​​​​.
#
# abs(x) denotes the absolute value of x.
#
# Example 1:
#
# Input: n = 25
#
# Output: 27
#
# Explanation:
#
# reverse(25) = 52.
#
# Thus, the answer is abs(25 - 52) = 27.
#
# Example 2:
#
# Input: n = 10
#
# Output: 9
#
# Explanation:
#
# reverse(10) = 01 which is 1.
#
# Thus, the answer is abs(10 - 1) = 9.
#
# Example 3:
#
# Input: n = 7
#
# Output: 0
#
# Explanation:
#
# reverse(7) = 7.
#
# Thus, the answer is abs(7 - 7) = 0.
#
# Constraints:
#
# 1 <= n <= 10^9
#

# @lc code=start
class Solution:
    def mirrorDistance(self, n: int) -> int:
        """
        Interview explanation:
        Mirror distance is |n - reverse_digits(n)| (leading zeros in the reverse
        drop naturally when forming the integer).

        Algorithm:
        - Build reverse by repeated mod/div 10; return abs(n - rev).

        Complexity: O(log n) time, O(1) space.
        """
        x, rev = n, 0
        while x:
            x, d = divmod(x, 10)
            rev = rev * 10 + d
        return abs(n - rev)

    def mirrorDistance_str(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: reverse via string slicing.

        Algorithm:
        - abs(n - int(str(n)[::-1])).

        Complexity: O(log n) time, O(log n) space.
        """
        return abs(n - int(str(n)[::-1]))
# @lc code=end
