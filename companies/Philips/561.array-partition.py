#
# @lc app=leetcode id=561 lang=python3
#
# [561] Array Partition
#
# https://leetcode.com/problems/array-partition/description/
#
# algorithms
# Easy (82.04%)
# Likes:    2449
# Dislikes: 306
# Total Accepted:    706K
# Total Submissions: 861K
# Testcase Example:  "[1,4,3,2]"
#
# Given an integer array nums of 2n integers, group these integers into n pairs
# (a_1, b_1), (a_2, b_2), ..., (a_n, b_n) such that the sum of min(a_i, b_i)
# for all i is maximized. Return the maximized sum.
#
# Example 1:
#
# Input: nums = [1,4,3,2]
# Output: 4
# Explanation: All possible pairings (ignoring the ordering of elements) are:
# 1. (1, 4), (2, 3) -> min(1, 4) + min(2, 3) = 1 + 2 = 3
# 2. (1, 3), (2, 4) -> min(1, 3) + min(2, 4) = 1 + 2 = 3
# 3. (1, 2), (3, 4) -> min(1, 2) + min(3, 4) = 1 + 3 = 4
# So the maximum possible sum is 4.
#
# Example 2:
#
# Input: nums = [6,2,6,5,1,2]
# Output: 9
# Explanation: The optimal pairing is (2, 1), (2, 5), (6, 6). min(2, 1) +
# min(2, 5) + min(6, 6) = 1 + 2 + 6 = 9.
#
# Constraints:
#
# 1 <= n <= 10^4
#
# nums.length == 2 * n
#
# -10^4 <= nums[i] <= 10^4
#


# @lc code=start
from typing import List
class Solution:
    def arrayPairSum(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Pairing adjacent numbers after sorting maximizes the sum of mins:
        each small value is paired with the next-smallest leftover, so we
        never "waste" a large number as the min of a pair.

        Algorithm:
        - Sort nums ascending.
        - Sum nums[0] + nums[2] + ... (every even index after sort).

        Complexity: O(n log n) time, O(n) or O(1) extra space depending on sort.
        """
        nums.sort()
        return sum(nums[i] for i in range(0, len(nums), 2))

    def arrayPairSumCounting(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Values are bounded in typical constraints (-10^4..10^4), so counting
        sort / frequency array gives linear time after offsetting negatives.

        Algorithm:
        - Count frequencies over the value range.
        - Walk values ascending, greedily take every other occurrence into the sum
          (same pairing as sorted adjacent pairs).

        Complexity: O(n + R) time, O(R) space for value range R.
        """
        OFFSET = 10000
        freq = [0] * (2 * OFFSET + 1)
        for x in nums:
            freq[x + OFFSET] += 1
        take = True
        ans = 0
        for v in range(len(freq)):
            while freq[v]:
                if take:
                    ans += v - OFFSET
                take = not take
                freq[v] -= 1
        return ans
# @lc code=end

