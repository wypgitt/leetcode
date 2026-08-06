#
# @lc app=leetcode id=3587 lang=python3
#
# [3587] Minimum Adjacent Swaps to Alternate Parity
#
# https://leetcode.com/problems/minimum-adjacent-swaps-to-alternate-parity/description/
#
# algorithms
# Medium (42.63%)
# Likes:    96
# Dislikes: 16
# Total Accepted:    21.3K
# Total Submissions: 50K
# Testcase Example:  "[2,4,6,5,7]"
#
#
# You are given an array nums of distinct integers.
#
# In one operation, you can swap any two adjacent elements in the array.
#
# An arrangement of the array is considered valid if the parity of
# adjacent elements alternates, meaning every pair of neighboring elements
# consists of one even and one odd number.
#
# Return the minimum number of adjacent swaps required to transform nums
# into any valid arrangement.
#
# If it is impossible to rearrange nums such that no two adjacent elements
# have the same parity, return -1.
#
# Example 1:
#
# Input: nums = [2,4,6,5,7]
#
# Output: 3
#
# Explanation:
#
# Swapping 5 and 6, the array becomes [2,4,5,6,7]
#
# Swapping 5 and 4, the array becomes [2,5,4,6,7]
#
# Swapping 6 and 7, the array becomes [2,5,4,7,6]. The array is now a
# valid arrangement. Thus, the answer is 3.
#
# Example 2:
#
# Input: nums = [2,4,5,7]
#
# Output: 1
#
# Explanation:
#
# By swapping 4 and 5, the array becomes [2,5,4,7], which is a valid
# arrangement. Thus, the answer is 1.
#
# Example 3:
#
# Input: nums = [1,2,3]
#
# Output: 0
#
# Explanation:
#
# The array is already a valid arrangement. Thus, no operations are
# needed.
#
# Example 4:
#
# Input: nums = [4,5,6,8]
#
# Output: -1
#
# Explanation:
#
# No valid arrangement is possible. Thus, the answer is -1.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# All elements in nums are distinct.
#

# @lc code=start

from typing import List


class Solution:
    def minSwaps(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternating parity needs |#odd - #even| ≤ 1. Adjacent swaps equal the
        total distance odds must move to their target parity slots.

        Algorithm:
        - If counts differ by >1 return -1.
        - Target odds on even indices (start even) and/or odd indices; cost is
          Σ|pos_odd - target_slot|; take the feasible minimum.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        odds = [i for i, x in enumerate(nums) if x % 2]
        odd_cnt, even_cnt = len(odds), n - len(odds)

        def cost(start: int) -> int:
            # place odds at start, start+2, ...
            return sum(abs(odds[j] - (start + 2 * j)) for j in range(len(odds)))

        if odd_cnt == even_cnt:
            return min(cost(0), cost(1))
        if odd_cnt == even_cnt + 1:
            return cost(0)
        if even_cnt == odd_cnt + 1:
            return cost(1)
        return -1
# @lc code=end
