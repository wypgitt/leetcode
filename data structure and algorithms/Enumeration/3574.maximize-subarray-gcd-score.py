#
# @lc app=leetcode id=3574 lang=python3
#
# [3574] Maximize Subarray GCD Score
#
# https://leetcode.com/problems/maximize-subarray-gcd-score/description/
#
# algorithms
# Hard (25.60%)
# Likes:    49
# Dislikes: 4
# Total Accepted:    6.5K
# Total Submissions: 25.5K
# Testcase Example:  "[2,4]\n1"
#
#
# You are given an array of positive integers nums and an integer k.
#
# You may perform at most k operations. In each operation, you can choose
# one element in the array and double its value. Each element can be
# doubled at most once.
#
# The score of a contiguous subarray is defined as the product of its
# length and the greatest common divisor (GCD) of all its elements.
#
# Your task is to return the maximum score that can be achieved by
# selecting a contiguous subarray from the modified array.
#
# Note:
#
# The greatest common divisor (GCD) of an array is the largest integer
# that evenly divides all the array elements.
#
# Example 1:
#
# Input: nums = [2,4], k = 1
#
# Output: 8
#
# Explanation:
#
# Double nums[0] to 4 using one operation. The modified array becomes [4,
# 4].
#
# The GCD of the subarray [4, 4] is 4, and the length is 2.
#
# Thus, the maximum possible score is 2 × 4 = 8.
#
# Example 2:
#
# Input: nums = [3,5,7], k = 2
#
# Output: 14
#
# Explanation:
#
# Double nums[2] to 14 using one operation. The modified array becomes [3,
# 5, 14].
#
# The GCD of the subarray [14] is 14, and the length is 1.
#
# Thus, the maximum possible score is 1 × 14 = 14.
#
# Example 3:
#
# Input: nums = [5,5,5], k = 1
#
# Output: 15
#
# Explanation:
#
# The subarray [5, 5, 5] has a GCD of 5, and its length is 3.
#
# Since doubling any element doesn't improve the score, the maximum score
# is 3 × 5 = 15.
#
# Constraints:
#
# 1 <= n == nums.length <= 1500
#
# 1 <= nums[i] <= 10^9
#
# 1 <= k <= n
#

# @lc code=start

from typing import List
from math import gcd, inf


class Solution:
    def maxGCDScore(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Doubling only multiplies GCD by at most 2. For a subarray, GCD becomes
        2·g iff we can double every element that currently has the minimum
        2-adic valuation — i.e. that min valuation's multiplicity ≤ k.

        Algorithm:
        - Precompute trailing-two counts cnt[i].
        - Enumerate all subarrays [l,r]; maintain running gcd, min cnt, and its
          frequency t; score = (g if t>k else 2g) * length.

        Complexity: O(n^2 log A) time, O(n) space.
        """
        n = len(nums)
        cnt = [0] * n
        for i, x in enumerate(nums):
            while x % 2 == 0:
                cnt[i] += 1
                x //= 2
        ans = 0
        for l in range(n):
            g = 0
            mi = inf
            t = 0
            for r in range(l, n):
                g = gcd(g, nums[r])
                if cnt[r] < mi:
                    mi = cnt[r]
                    t = 1
                elif cnt[r] == mi:
                    t += 1
                score_g = g if t > k else g * 2
                ans = max(ans, score_g * (r - l + 1))
        return ans
# @lc code=end
