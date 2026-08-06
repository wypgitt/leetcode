#
# @lc app=leetcode id=3818 lang=python3
#
# [3818] Minimum Prefix Removal to Make Array Strictly Increasing
#
# https://leetcode.com/problems/minimum-prefix-removal-to-make-array-strictly-increasing/description/
#
# algorithms
# Medium (74.09%)
# Likes:    56
# Dislikes: 7
# Total Accepted:    53.6K
# Total Submissions: 72.4K
# Testcase Example:  "[1,-1,2,3,3,4,5]"
#
#
# You are given an integer array nums.
#
# You need to remove exactly one prefix (possibly empty) from nums.
#
# Return an integer denoting the minimum length of the removed prefix such
# that the remaining array is strictly increasing.
#
# Example 1:
#
# Input: nums = [1,-1,2,3,3,4,5]
#
# Output: 4
#
# Explanation:
#
# Removing the prefix = [1, -1, 2, 3] leaves the remaining array [3, 4, 5]
# which is strictly increasing.
#
# Example 2:
#
# Input: nums = [4,3,-2,-5]
#
# Output: 3
#
# Explanation:
#
# Removing the prefix = [4, 3, -2] leaves the remaining array [-5] which
# is strictly increasing.
#
# Example 3:
#
# Input: nums = [1,2,3,4]
#
# Output: 0
#
# Explanation:
#
# The array nums = [1, 2, 3, 4] is already strictly increasing so removing
# an empty prefix is sufficient.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^9 <= nums[i] <= 10^9​​​​​​​
#

# @lc code=start

from typing import List


class Solution:
    def minimumPrefixLength(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Remaining array after removing a prefix must be strictly increasing;
        minimize the removed length = maximize the strictly increasing
        suffix.

        Algorithm:
        - Walk left from the end while nums[i-1] < nums[i]; the first break
          index is the answer.

        Complexity: O(n) time, O(1) space.
        """
        i = len(nums) - 1
        while i > 0 and nums[i - 1] < nums[i]:
            i -= 1
        return i

    def minimumPrefixLength_scan(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: find the leftmost position where the suffix from there is
        strictly increasing by scanning drops from the right.

        Algorithm:
        - Same right-to-left scan; return that start index.

        Complexity: O(n) time, O(1) space.
        """
        n = len(nums)
        for i in range(n - 1, 0, -1):
            if nums[i - 1] >= nums[i]:
                return i
        return 0
# @lc code=end
