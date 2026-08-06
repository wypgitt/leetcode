#
# @lc app=leetcode id=2941 lang=python3
#
# [2941] Maximum GCD-Sum of a Subarray
#
# https://leetcode.com/problems/maximum-gcd-sum-of-a-subarray/description/
#
# algorithms
# Hard (39.43%)
# Likes:    17
# Dislikes: 3
# Total Accepted:    739
# Total Submissions: 1.9K
# Testcase Example:  "[2,1,4,4,4,2]\n2"
#
#
# You are given an array of integers nums and an integer k.
#
# The gcd-sum of an array a is calculated as follows:
#
# Let s be the sum of all the elements of a.
#
# Let g be the greatest common divisor of all the elements of a.
#
# The gcd-sum of a is equal to s * g.
#
# Return the maximum gcd-sum of a subarray of nums with at least k
# elements.
#
# Example 1:
#
# Input: nums = [2,1,4,4,4,2], k = 2
# Output: 48
# Explanation: We take the subarray [4,4,4], the gcd-sum of this array is
# 4 * (4 + 4 + 4) = 48.
# It can be shown that we can not select any other subarray with a gcd-sum
# greater than 48.
#
# Example 2:
#
# Input: nums = [7,3,9,4], k = 1
# Output: 81
# Explanation: We take the subarray [9], the gcd-sum of this array is 9 *
# 9 = 81.
# It can be shown that we can not select any other subarray with a gcd-sum
# greater than 81.
#
# Constraints:
#
# n == nums.length
#
# 1 <= n <= 10^5
#
# 1 <= nums[i] <= 10^6
#
# 1 <= k <= n
#
# @lc code=start

from typing import List
from math import gcd
from itertools import accumulate


class Solution:
    def maxGcdSum(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Premium: maximize (subarray sum) * (subarray gcd) over contiguous subarrays
        of length >= k. For fixed right end, distinct GCDs of prefixes are O(log A).

        Algorithm:
        - Maintain list of (leftmost start, gcd) for subarrays ending at i; merge
          equal gcds; use prefix sums to evaluate length>=k candidates.

        Complexity: O(n log A) time, O(n) space.
        """
        ans = 0
        segs: List[tuple] = []
        prefix = list(accumulate(nums, initial=0))
        for i, v in enumerate(nums):
            nxt: List[tuple] = []
            for start, g in segs:
                ng = gcd(g, v)
                if not nxt or nxt[-1][1] != ng:
                    nxt.append((start, ng))
            segs = nxt
            segs.append((i, v))
            for start, g in segs:
                if i - start + 1 >= k:
                    ans = max(ans, (prefix[i + 1] - prefix[start]) * g)
        return ans
# @lc code=end

