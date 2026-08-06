#
# @lc app=leetcode id=3761 lang=python3
#
# [3761] Minimum Absolute Distance Between Mirror Pairs
#
# https://leetcode.com/problems/minimum-absolute-distance-between-mirror-pairs/description/
#
# algorithms
# Medium (59.19%)
# Likes:    404
# Dislikes: 16
# Total Accepted:    117.2K
# Total Submissions: 198.1K
# Testcase Example:  "[12,21,45,33,54]"
#
#
# You are given an integer array nums.
#
# A mirror pair is a pair of indices (i, j) such that:
#
# 0 <= i < j < nums.length, and
#
# reverse(nums[i]) == nums[j], where reverse(x) denotes the integer formed
# by reversing the digits of x. Leading zeros are omitted after reversing,
# for example reverse(120) = 21.
#
# Return the minimum absolute distance between the indices of any mirror
# pair. The absolute distance between indices i and j is abs(i - j).
#
# If no mirror pair exists, return -1.
#
# Example 1:
#
# Input: nums = [12,21,45,33,54]
#
# Output: 1
#
# Explanation:
#
# The mirror pairs are:
#
# (0, 1) since reverse(nums[0]) = reverse(12) = 21 = nums[1], giving an
# absolute distance abs(0 - 1) = 1.
#
# (2, 4) since reverse(nums[2]) = reverse(45) = 54 = nums[4], giving an
# absolute distance abs(2 - 4) = 2.
#
# The minimum absolute distance among all pairs is 1.
#
# Example 2:
#
# Input: nums = [120,21]
#
# Output: 1
#
# Explanation:
#
# There is only one mirror pair (0, 1) since reverse(nums[0]) =
# reverse(120) = 21 = nums[1].
#
# The minimum absolute distance is 1.
#
# Example 3:
#
# Input: nums = [21,120]
#
# Output: -1
#
# Explanation:
#
# There are no mirror pairs in the array.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9​​​​​​​
#

# @lc code=start
from typing import List


class Solution:
    def minMirrorPairDistance(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Pair (i, j) with i < j and reverse(nums[i]) == nums[j]. Minimize j - i.
        reverse drops leading zeros (e.g. reverse(120) = 21).

        Algorithm:
        - Map key = reverse(value) -> latest index. At j, look up nums[j] to find
          an i with reverse(nums[i]) == nums[j]; track min distance.

        Complexity: O(n log A) time for reversing digits, O(n) space.
        """
        def rev(x: int) -> int:
            r = 0
            while x:
                x, d = divmod(x, 10)
                r = r * 10 + d
            return r

        last = {}
        ans = float("inf")
        for j, v in enumerate(nums):
            if v in last:
                ans = min(ans, j - last[v])
            last[rev(v)] = j
        return -1 if ans == float("inf") else ans
# @lc code=end
