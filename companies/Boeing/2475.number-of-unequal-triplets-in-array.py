#
# @lc app=leetcode id=2475 lang=python3
#
# [2475] Number of Unequal Triplets in Array
#
# https://leetcode.com/problems/number-of-unequal-triplets-in-array/description/
#
# algorithms
# Easy (73.50%)
# Likes:    462
# Dislikes: 50
# Total Accepted:    65.2K
# Total Submissions: 88.7K
# Testcase Example:  "[4,4,2,4,3]"
#
# You are given a 0-indexed array of positive integers nums. Find the number of
# triplets (i, j, k) that meet the following conditions:
#
#
# 0 <= i < j < k < nums.length
#
#
# nums[i], nums[j], and nums[k] are pairwise distinct.
#
#
#
# In other words, nums[i] != nums[j], nums[i] != nums[k], and nums[j] !=
# nums[k].
#
#
#
#
#
# Return the number of triplets that meet the conditions.
#
#
#
# Example 1:
#
# Input: nums = [4,4,2,4,3]
# Output: 3
# Explanation: The following triplets meet the conditions:
# - (0, 2, 4) because 4 != 2 != 3
# - (1, 2, 4) because 4 != 2 != 3
# - (2, 3, 4) because 2 != 4 != 3
# Since there are 3 triplets, we return 3.
# Note that (2, 0, 4) is not a valid triplet because 2 > 0.
#
# Example 2:
#
# Input: nums = [1,1,1,1,1]
# Output: 0
# Explanation: No triplets meet the conditions so we return 0.
#
#
#
# Constraints:
#
#
# 3 <= nums.length <= 100
#
#
# 1 <= nums[i] <= 1000
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def unequalTriplets(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Count triplets (i<j<k) with nums[i], nums[j], nums[k] all different.

        Algorithm:
        - Total C(n,3) minus triplets with <3 distinct values via frequencies:
          for each value mid of a scan, left*count*right for distinct triples.

        Complexity: O(n) time, O(n) space.
        """
        cnt = Counter(nums)
        ans = left = 0
        n = len(nums)
        for c in cnt.values():
            right = n - left - c
            ans += left * c * right
            left += c
        return ans

    def unequalTriplets_math(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: C(n,3) - same-value and two-value contributions.

        Algorithm:
        - Subtract C(freq,3) and C(freq,2)*(n-freq) for each value.

        Complexity: O(n) time, O(n) space.
        """
        from math import comb

        n = len(nums)
        ans = comb(n, 3)
        for c in Counter(nums).values():
            ans -= comb(c, 3)
            ans -= comb(c, 2) * (n - c)
        return ans
# @lc code=end

