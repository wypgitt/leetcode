#
# @lc app=leetcode id=3431 lang=python3
#
# [3431] Minimum Unlocked Indices to Sort Nums
#
# https://leetcode.com/problems/minimum-unlocked-indices-to-sort-nums/description/
#
# algorithms
# Medium (57.32%)
# Likes:    6
# Dislikes: 3
# Total Accepted:    591
# Total Submissions: 1K
# Testcase Example:  "[1,2,1,2,3,2]\n[1,0,1,1,0,1]"
#
#
# You are given an array nums consisting of integers between 1 and 3, and
# a binary array locked of the same size.
#
# We consider nums sortable if it can be sorted using adjacent swaps,
# where a swap between two indices i and i + 1 is allowed if nums[i] -
# nums[i + 1] == 1 and locked[i] == 0.
#
# In one operation, you can unlock any index i by setting locked[i] to 0.
#
# Return the minimum number of operations needed to make nums sortable. If
# it is not possible to make nums sortable, return -1.
#
# Example 1:
#
# Input: nums = [1,2,1,2,3,2], locked = [1,0,1,1,0,1]
#
# Output: 0
#
# Explanation:
#
# We can sort nums using the following swaps:
#
# swap indices 1 with 2
#
# swap indices 4 with 5
#
# So, there is no need to unlock any index.
#
# Example 2:
#
# Input: nums = [1,2,1,1,3,2,2], locked = [1,0,1,1,0,1,0]
#
# Output: 2
#
# Explanation:
#
# If we unlock indices 2 and 5, we can sort nums using the following
# swaps:
#
# swap indices 1 with 2
#
# swap indices 2 with 3
#
# swap indices 4 with 5
#
# swap indices 5 with 6
#
# Example 3:
#
# Input: nums = [1,2,1,2,3,2,1], locked = [0,0,0,0,0,0,0]
#
# Output: -1
#
# Explanation:
#
# Even if all indices are unlocked, it can be shown that nums is not
# sortable.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 3
#
# locked.length == nums.length
#
# 0 <= locked[i] <= 1
#

# @lc code=start
from typing import List


class Solution:
    def minUnlockedIndices(self, nums: List[int], locked: List[int]) -> int:
        """
        Interview explanation:
        Values are only 1/2/3; allowed swaps only exchange (2,1) or (3,2) across an
        unlocked index. Sorting is impossible iff some 3 sits left of some 1.
        Otherwise unlock every locked barrier between the first 2 and last 1, and
        between the first 3 and last 2.

        Algorithm:
        - If first 3 index < last 1 index: return -1.
        - Count locked[i]==1 for i in [first2, last1) and [first3, last2).

        Complexity: O(n) time, O(1) space.
        """
        first2 = next((i for i, x in enumerate(nums) if x == 2), -1)
        first3 = next((i for i, x in enumerate(nums) if x == 3), -1)
        last1 = next((i for i, x in reversed(list(enumerate(nums))) if x == 1), -1)
        last2 = next((i for i, x in reversed(list(enumerate(nums))) if x == 2), -1)
        if first3 != -1 and last1 != -1 and first3 < last1:
            return -1
        ans = 0
        if first2 != -1 and last1 != -1:
            ans += sum(locked[i] == 1 for i in range(first2, last1))
        if first3 != -1 and last2 != -1:
            ans += sum(locked[i] == 1 for i in range(first3, last2))
        return ans
# @lc code=end
