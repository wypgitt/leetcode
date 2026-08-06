#
# @lc app=leetcode id=3729 lang=python3
#
# [3729] Count Distinct Subarrays Divisible by K in Sorted Array
#
# https://leetcode.com/problems/count-distinct-subarrays-divisible-by-k-in-sorted-array/description/
#
# algorithms
# Hard (28.30%)
# Likes:    63
# Dislikes: 3
# Total Accepted:    6.3K
# Total Submissions: 22.4K
# Testcase Example:  "[1,2,3]\n3"
#
#
# You are given an integer array nums sorted in non-descending order and a
# positive integer k.
#
# A subarray of nums is good if the sum of its elements is divisible by k.
#
# Return an integer denoting the number of distinct good subarrays of
# nums.
#
# Subarrays are distinct if their sequences of values are. For example,
# there are 3 distinct subarrays in [1, 1, 1], namely [1], [1, 1], and [1,
# 1, 1].
#
# Example 1:
#
# Input: nums = [1,2,3], k = 3
#
# Output: 3
#
# Explanation:
#
# The good subarrays are [1, 2], [3], and [1, 2, 3]. For example, [1, 2,
# 3] is good because the sum of its elements is 1 + 2 + 3 = 6, and 6 % k =
# 6 % 3 = 0.
#
# Example 2:
#
# Input: nums = [2,2,2,2,2,2], k = 6
#
# Output: 2
#
# Explanation:
#
# The good subarrays are [2, 2, 2] and [2, 2, 2, 2, 2, 2]. For example,
# [2, 2, 2] is good because the sum of its elements is 2 + 2 + 2 = 6, and
# 6 % k = 6 % 6 = 0.
#
# Note that [2, 2, 2] is counted only once.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# nums is sorted in non-descending order.
#
# 1 <= k <= 10^9
#

# @lc code=start
from collections import Counter
from typing import List


class Solution:
    def numGoodSubarrays(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Count all subarrays with sum % k == 0 via prefix remainders, then remove
        duplicates. In a sorted array the only duplicate contents are constant
        runs of equal values.

        Algorithm:
        - Classic remainder Counter for total good subarrays.
        - For each run of value v length m, for each good length h
          (h*v % k == 0), subtract (m - h) extra copies.

        Complexity: O(n + sum run lengths) = O(n) time, O(n) space.
        """
        cnt = Counter({0: 1})
        ans = s = 0
        for x in nums:
            s = (s + x) % k
            ans += cnt[s]
            cnt[s] += 1
        n = len(nums)
        i = 0
        while i < n:
            j = i + 1
            while j < n and nums[j] == nums[i]:
                j += 1
            m = j - i
            for h in range(1, m + 1):
                if (h * nums[i]) % k == 0:
                    ans -= m - h
            i = j
        return ans

    def numGoodSubarrays_gcd_step(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: same prefix count; for runs, step h by k/gcd(k, v).

        Algorithm:
        - step = k // gcd(k, v); subtract extras for h = step, 2*step, ...

        Complexity: O(n) time, O(n) space.
        """
        from math import gcd

        cnt = Counter({0: 1})
        ans = s = 0
        for x in nums:
            s = (s + x) % k
            ans += cnt[s]
            cnt[s] += 1
        n = len(nums)
        i = 0
        while i < n:
            j = i + 1
            while j < n and nums[j] == nums[i]:
                j += 1
            m, v = j - i, nums[i]
            step = k // gcd(k, v % k)
            h = step
            while h <= m:
                ans -= m - h
                h += step
            i = j
        return ans
# @lc code=end

