#
# @lc app=leetcode id=3920 lang=python3
#
# [3920] Maximize Fixed Points After Deletions
#
# https://leetcode.com/problems/maximize-fixed-points-after-deletions/description/
#
# algorithms
# Hard (19.91%)
# Likes:    57
# Dislikes: 1
# Total Accepted:    5.9K
# Total Submissions: 29.8K
# Testcase Example:  "[0,2,1]"
#
#
# You are given an integer array nums.
#
# A position i is called a fixed point if nums[i] == i.
#
# You are allowed to delete any number of elements (including zero) from
# the array. After each deletion, the remaining elements shift left, and
# indices are reassigned starting from 0.
#
# Return an integer denoting the maximum number of fixed points that can
# be achieved after performing any number of deletions.
#
# Example 1:
#
# Input: nums = [0,2,1]
#
# Output: 2
#
# Explanation:
#
# Delete nums[1] = 2. The array becomes [0, 1].
#
# Now, nums[0] = 0 and nums[1] = 1, so both indices are fixed points.
#
# Thus, the answer is 2.
#
# Example 2:
#
# Input: nums = [3,1,2]
#
# Output: 2
#
# Explanation:
#
# Do not delete any elements. The array remains [3, 1, 2].
#
# Here, nums[1] = 1 and nums[2] = 2, so these indices are fixed points.
#
# Thus, the answer is 2.
#
# Example 3:
#
# Input: nums = [1,0,1,2]
#
# Output: 3
#
# Explanation:
#
# Delete nums[0] = 1. The array becomes [0, 1, 2].
#
# Now, nums[0] = 0, nums[1] = 1, and nums[2] = 2, so all indices are fixed
# points.
#
# Thus, the answer is 3.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 0 <= nums[i] <= 10^5
#

# @lc code=start
from collections import defaultdict
from typing import List


class FenwickMax:
    def __init__(self, size: int) -> None:
        """
        Interview explanation:
        Fenwick tree storing prefix maxima (for LIS-style DP over deletions).

        Algorithm:
        - 1-indexed tree initialized to zeros.

        Complexity: O(size) space.
        """
        self.tree = [0] * (size + 1)

    def update(self, index: int, value: int) -> None:
        """
        Interview explanation:
        Point update: raise tree entries covering index to at least value.

        Algorithm:
        - Climb by lowbit, keeping max at each node.

        Complexity: O(log n) time, O(1) space.
        """
        index += 1
        while index < len(self.tree):
            if value > self.tree[index]:
                self.tree[index] = value
            index += index & -index

    def query(self, index: int) -> int:
        """
        Interview explanation:
        Prefix maximum over ranks in [0, index].

        Algorithm:
        - Descend by lowbit taking max.

        Complexity: O(log n) time, O(1) space.
        """
        index += 1
        best = 0
        while index > 0:
            if self.tree[index] > best:
                best = self.tree[index]
            index -= index & -index
        return best


class Solution:
    def maxFixedPoints(self, nums: List[int]) -> int:
        """
        Interview explanation:
        After deletions (remaining elements shift left), maximize how many
        positions satisfy nums'[i] == i.

        Algorithm:
        - Value v can become fixed only if we delete exactly i-v elements before
          original index i (and v <= i). Group candidates by value v.
        - Process values in increasing order; DP[deletes] = max chain length via
          a Fenwick of maxima on the deletion count.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(nums)
        groups = defaultdict(list)

        for i, value in enumerate(nums):
            if value <= i:
                groups[value].append(i - value)

        bit = FenwickMax(n)
        ans = 0

        for value in sorted(groups):
            pending = []
            for deleted_before in groups[value]:
                best = bit.query(deleted_before) + 1
                pending.append((deleted_before, best))
                if best > ans:
                    ans = best

            for deleted_before, best in pending:
                bit.update(deleted_before, best)

        return ans
# @lc code=end
