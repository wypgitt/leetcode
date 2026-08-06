#
# @lc app=leetcode id=3091 lang=python3
#
# [3091] Apply Operations to Make Sum of Array Greater Than or Equal to k
#
# https://leetcode.com/problems/apply-operations-to-make-sum-of-array-greater-than-or-equal-to-k/description/
#
# algorithms
# Medium (44.61%)
# Likes:    178
# Dislikes: 19
# Total Accepted:    33.5K
# Total Submissions: 75K
# Testcase Example:  "11"
#
#
# You are given a positive integer k. Initially, you have an array nums =
# [1].
#
# You can perform any of the following operations on the array any number
# of times (possibly zero):
#
# Choose any element in the array and increase its value by 1.
#
# Duplicate any element in the array and add it to the end of the array.
#
# Return the minimum number of operations required to make the sum of
# elements of the final array greater than or equal to k.
#
# Example 1:
#
# Input: k = 11
#
# Output: 5
#
# Explanation:
#
# We can do the following operations on the array nums = [1]:
#
# Increase the element by 1 three times. The resulting array is nums =
# [4].
#
# Duplicate the element two times. The resulting array is nums = [4,4,4].
#
# The sum of the final array is 4 + 4 + 4 = 12 which is greater than or
# equal to k = 11.
#
# The total number of operations performed is 3 + 2 = 5.
#
# Example 2:
#
# Input: k = 1
#
# Output: 0
#
# Explanation:
#
# The sum of the original array is already greater than or equal to 1, so
# no operations are needed.
#
# Constraints:
#
# 1 <= k <= 10^5
#

# @lc code=start
import math


class Solution:
    def minOperations(self, k: int) -> int:
        """
        Interview explanation:
        Start from [1]. Optimal: increment one value up to x, then duplicate it
        enough times so x * copies >= k.

        Algorithm:
        - For each x in 1..k: ops = (x - 1) + (ceil(k/x) - 1); take minimum.

        Complexity: O(k) time, O(1) space.
        """
        ans = k - 1
        for x in range(1, k + 1):
            ans = min(ans, (x - 1) + (math.ceil(k / x) - 1))
        return ans

    def minOperations_by_copies(self, k: int) -> int:
        """
        Interview explanation:
        Dual view: choose how many final copies c of value x = ceil(k/c).

        Algorithm:
        - For each copy count c, x = ceil(k/c); ops = (x - 1) + (c - 1).

        Complexity: O(k) time, O(1) space.
        """
        ans = k - 1
        for copies in range(1, k + 1):
            x = (k + copies - 1) // copies
            ans = min(ans, (x - 1) + (copies - 1))
        return ans
# @lc code=end
