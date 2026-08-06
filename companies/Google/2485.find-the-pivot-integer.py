#
# @lc app=leetcode id=2485 lang=python3
#
# [2485] Find the Pivot Integer
#
# https://leetcode.com/problems/find-the-pivot-integer/description/
#
# algorithms
# Easy (83.73%)
# Likes:    1478
# Dislikes: 60
# Total Accepted:    327.2K
# Total Submissions: 390.7K
# Testcase Example:  "8"
#
# Given a positive integer n, find the pivot integer x such that:
#
#
# The sum of all elements between 1 and x inclusively equals the sum of all
# elements between x and n inclusively.
#
# Return the pivot integer x. If no such integer exists, return -1. It is
# guaranteed that there will be at most one pivot index for the given input.
#
#
#
# Example 1:
#
# Input: n = 8
# Output: 6
# Explanation: 6 is the pivot integer since: 1 + 2 + 3 + 4 + 5 + 6 = 6 + 7 + 8 =
# 21.
#
# Example 2:
#
# Input: n = 1
# Output: 1
# Explanation: 1 is the pivot integer since: 1 = 1.
#
# Example 3:
#
# Input: n = 4
# Output: -1
# Explanation: It can be proved that no such integer exist.
#
#
#
# Constraints:
#
#
# 1 <= n <= 1000
#

# @lc code=start
class Solution:
    def pivotInteger(self, n: int) -> int:
        """
        Interview explanation:
        Find x in 1..n with sum(1..x) == sum(x..n), else -1.

        Algorithm:
        - sum(1..x)=x*(x+1)/2; total=n*(n+1)/2; equate => x*x = total; check square.

        Complexity: O(1) time.
        """
        total = n * (n + 1) // 2
        x = int(total**0.5)
        return x if x * x == total else -1

    def pivotInteger_math(self, n: int) -> int:
        """
        Interview explanation:
        Alternate binary search on x.

        Algorithm:
        - Search x where 2*x*(x+1)/2 == total + x.

        Complexity: O(log n) time.
        """
        lo, hi = 1, n
        total = n * (n + 1) // 2
        while lo <= hi:
            mid = (lo + hi) // 2
            left = mid * (mid + 1) // 2
            right = total - left + mid
            if left == right:
                return mid
            if left < right:
                lo = mid + 1
            else:
                hi = mid - 1
        return -1
# @lc code=end

