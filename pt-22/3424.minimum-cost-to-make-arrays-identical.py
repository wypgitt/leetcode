#
# @lc app=leetcode id=3424 lang=python3
#
# [3424] Minimum Cost to Make Arrays Identical
#
# https://leetcode.com/problems/minimum-cost-to-make-arrays-identical/description/
#
# algorithms
# Medium (38.12%)
# Likes:    90
# Dislikes: 13
# Total Accepted:    25.9K
# Total Submissions: 67.9K
# Testcase Example:  "[-7,9,5]\n[7,-2,-5]\n2"
#
#
# You are given two integer arrays arr and brr of length n, and an integer
# k. You can perform the following operations on arr any number of times:
#
# Split arr into any number of contiguous subarrays and rearrange these
# subarrays in any order. This operation has a fixed cost of k.
#
# Choose any element in arr and add or subtract a positive integer x to
# it. The cost of this operation is x.
#
# Return the minimum total cost to make arr equal to brr.
#
# Example 1:
#
# Input: arr = [-7,9,5], brr = [7,-2,-5], k = 2
#
# Output: 13
#
# Explanation:
#
# Split arr into two contiguous subarrays: [-7] and [9, 5] and rearrange
# them as [9, 5, -7], with a cost of 2.
#
# Subtract 2 from element arr[0]. The array becomes [7, 5, -7]. The cost
# of this operation is 2.
#
# Subtract 7 from element arr[1]. The array becomes [7, -2, -7]. The cost
# of this operation is 7.
#
# Add 2 to element arr[2]. The array becomes [7, -2, -5]. The cost of this
# operation is 2.
#
# The total cost to make the arrays equal is 2 + 2 + 7 + 2 = 13.
#
# Example 2:
#
# Input: arr = [2,1], brr = [2,1], k = 0
#
# Output: 0
#
# Explanation:
#
# Since the arrays are already equal, no operations are needed, and the
# total cost is 0.
#
# Constraints:
#
# 1 <= arr.length == brr.length <= 10^5
#
# 0 <= k <= 2 * 10^10
#
# -10^5 <= arr[i] <= 10^5
#
# -10^5 <= brr[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def minCost(self, arr: List[int], brr: List[int], k: int) -> int:
        """
        Interview explanation:
        Element edits cost |arr[i]-brr[i]| in place. Rearranging contiguous blocks
        for cost k is equivalent (for matching) to fully sorting both arrays once,
        then pairing by rank — so compare no-rearrange vs sort-both + k.

        Algorithm:
        - cost0 = sum |arr[i]-brr[i]| without rearrange.
        - cost1 = sum |sorted(arr)[i]-sorted(brr)[i]| + k.
        - Return min(cost0, cost1).

        Complexity: O(n log n) time, O(n) space.
        """
        def cost(a: List[int], b: List[int]) -> int:
            return sum(abs(x - y) for x, y in zip(a, b))

        return min(cost(arr, brr), cost(sorted(arr), sorted(brr)) + k)
# @lc code=end
