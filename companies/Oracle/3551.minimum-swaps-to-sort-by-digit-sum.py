#
# @lc app=leetcode id=3551 lang=python3
#
# [3551] Minimum Swaps to Sort by Digit Sum
#
# https://leetcode.com/problems/minimum-swaps-to-sort-by-digit-sum/description/
#
# algorithms
# Medium (50.76%)
# Likes:    155
# Dislikes: 6
# Total Accepted:    26.8K
# Total Submissions: 52.8K
# Testcase Example:  "[37,100]"
#
#
# You are given an array nums of distinct positive integers. You need to
# sort the array in increasing order based on the sum of the digits of
# each number. If two numbers have the same digit sum, the smaller number
# appears first in the sorted order.
#
# Return the minimum number of swaps required to rearrange nums into this
# sorted order.
#
# A swap is defined as exchanging the values at two distinct positions in
# the array.
#
# Example 1:
#
# Input: nums = [37,100]
#
# Output: 1
#
# Explanation:
#
# Compute the digit sum for each integer: [3 + 7 = 10, 1 + 0 + 0 = 1] →
# [10, 1]
#
# Sort the integers based on digit sum: [100, 37]. Swap 37 with 100 to
# obtain the sorted order.
#
# Thus, the minimum number of swaps required to rearrange nums is 1.
#
# Example 2:
#
# Input: nums = [22,14,33,7]
#
# Output: 0
#
# Explanation:
#
# Compute the digit sum for each integer: [2 + 2 = 4, 1 + 4 = 5, 3 + 3 =
# 6, 7 = 7] → [4, 5, 6, 7]
#
# Sort the integers based on digit sum: [22, 14, 33, 7]. The array is
# already sorted.
#
# Thus, the minimum number of swaps required to rearrange nums is 0.
#
# Example 3:
#
# Input: nums = [18,43,34,16]
#
# Output: 2
#
# Explanation:
#
# Compute the digit sum for each integer: [1 + 8 = 9, 4 + 3 = 7, 3 + 4 =
# 7, 1 + 6 = 7] → [9, 7, 7, 7]
#
# Sort the integers based on digit sum: [16, 34, 43, 18]. Swap 18 with 16,
# and swap 43 with 34 to obtain the sorted order.
#
# Thus, the minimum number of swaps required to rearrange nums is 2.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# nums consists of distinct positive integers.
#

# @lc code=start
from typing import List


class Solution:
    def minSwaps(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Target order is nums sorted by (digit_sum, value). Min swaps to realize
        a permutation equals n - number of cycles in that permutation.

        Algorithm:
        - Build sorted target array; map value → current index.
        - Walk cycles of positions; each cycle of length L costs L - 1 swaps.

        Complexity: O(n log n) time, O(n) space.
        """
        def digit_sum(x: int) -> int:
            s = 0
            while x:
                s += x % 10
                x //= 10
            return s

        n = len(nums)
        target = sorted(nums, key=lambda x: (digit_sum(x), x))
        pos = {v: i for i, v in enumerate(nums)}
        seen = [False] * n
        swaps = 0
        for i in range(n):
            if seen[i] or target[i] == nums[i]:
                continue
            j = i
            length = 0
            while not seen[j]:
                seen[j] = True
                j = pos[target[j]]
                length += 1
            swaps += length - 1
        return swaps
# @lc code=end
