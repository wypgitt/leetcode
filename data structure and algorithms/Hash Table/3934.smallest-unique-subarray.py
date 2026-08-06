#
# @lc app=leetcode id=3934 lang=python3
#
# [3934] Smallest Unique Subarray
#
# https://leetcode.com/problems/smallest-unique-subarray/description/
#
# algorithms
# Hard (41.05%)
# Likes:    64
# Dislikes: 5
# Total Accepted:    8.2K
# Total Submissions: 20.1K
# Testcase Example:  "[3,3,3]"
#
#
# You are given an integer array nums.
#
# Find the minimum length of a subarray that is not identical to any other
# subarray in nums.
#
# Return an integer denoting the minimum possible length of such a
# subarray.
#
# Two subarrays are considered identical if they have the same length and
# the same elements in corresponding positions.
#
# Example 1:
#
# Input: nums = [3,3,3]
#
# Output: 3
#
# Explanation:
#
# Subarrays of length 1: [3] → appears 3 times
#
# Subarrays of length 2: [3, 3] → appears 2 times
#
# Subarrays of length 3: [3, 3, 3] → appears once
#
# The subarray [3, 3, 3] is unique, so the smallest unique subarray length
# is 3.
#
# Example 2:
#
# Input: nums = [2,1,2,3,3]
#
# Output: 1
#
# Explanation:
#
# Subarrays of length 1:
#
# [2] → appears 2 times
#
# [1] → appears once
#
# [3] → appears 2 times
#
# The subarray [1] is unique, so the smallest unique subarray length is 1.
#
# Example 3:
#
# Input: nums = [1,1,2,2,1]
#
# Output: 2
#
# Explanation:
#
# Subarrays of length 1:
#
# [1] → appears 3 times
#
# [2] → appears 2 times
#
# Subarrays of length 2:
#
# [1, 1] → appears once
#
# [1, 2] → appears once
#
# [2, 2] → appears once
#
# [2, 1] → appears once
#
# There is at least one subarray of length 2 that is unique, so the
# smallest unique subarray length is 2.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start

from typing import List
from collections import defaultdict


class Solution:
    def smallestUniqueSubarray(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Uniqueness is monotonic in length: if some length-L subarray is unique,
        every longer subarray that extends it is unique too. Binary-search the
        minimal L and test with double rolling hashes.

        Algorithm:
        - Binary search length L in [1, n].
        - For fixed L, slide two modular hashes; if any hash-pair occurs once,
          L is feasible.
        - Return the smallest feasible L (n always works).

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(nums)
        BASE1, MOD1 = 911382323, 1_000_000_007
        BASE2, MOD2 = 972663749, 1_000_000_009

        def has_unique(length: int) -> bool:
            if length == n:
                return True
            pow1 = pow(BASE1, length, MOD1)
            pow2 = pow(BASE2, length, MOD2)
            h1 = h2 = 0
            for i in range(length):
                h1 = (h1 * BASE1 + nums[i]) % MOD1
                h2 = (h2 * BASE2 + nums[i]) % MOD2
            freq = defaultdict(int)
            freq[(h1, h2)] += 1
            for i in range(length, n):
                h1 = (h1 * BASE1 + nums[i]) % MOD1
                h1 = (h1 - nums[i - length] * pow1) % MOD1
                h2 = (h2 * BASE2 + nums[i]) % MOD2
                h2 = (h2 - nums[i - length] * pow2) % MOD2
                freq[(h1, h2)] += 1
            return any(v == 1 for v in freq.values())

        lo, hi, ans = 1, n, n
        while lo <= hi:
            mid = (lo + hi) // 2
            if has_unique(mid):
                ans = mid
                hi = mid - 1
            else:
                lo = mid + 1
        return ans
# @lc code=end
