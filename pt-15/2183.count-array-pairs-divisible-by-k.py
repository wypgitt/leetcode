#
# @lc app=leetcode id=2183 lang=python3
#
# [2183] Count Array Pairs Divisible by K
#
# https://leetcode.com/problems/count-array-pairs-divisible-by-k/description/
#
# algorithms
# Hard (31.01%)
# Likes:    936
# Dislikes: 39
# Total Accepted:    24.8K
# Total Submissions: 79.9K
# Testcase Example:  "[1,2,3,4,5]\n2"
#
# Given a 0-indexed integer array nums of length n and an integer k, return the
# number of pairs (i, j) such that:
#
#
# 0 <= i < j <= n - 1 and
#
#
# nums[i] * nums[j] is divisible by k.
#
#
#
# Example 1:
#
# Input: nums = [1,2,3,4,5], k = 2
# Output: 7
# Explanation:
# The 7 pairs of indices whose corresponding products are divisible by 2 are
# (0, 1), (0, 3), (1, 2), (1, 3), (1, 4), (2, 3), and (3, 4).
# Their products are 2, 4, 6, 8, 10, 12, and 20 respectively.
# Other pairs such as (0, 2) and (2, 4) have products 3 and 15 respectively,
# which are not divisible by 2.
#
# Example 2:
#
# Input: nums = [1,2,3,4], k = 5
# Output: 0
# Explanation: There does not exist any pair of indices whose corresponding
# product is divisible by 5.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 1 <= nums[i], k <= 10^5
#

# @lc code=start
from typing import List
from collections import Counter
from math import gcd


class Solution:
    def countPairs(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Count pairs i < j with (nums[i] * nums[j]) % k == 0.

        Algorithm:
        (gcd / divisors)
        - Let g_i = gcd(nums[i], k). Pair (i,j) works iff g_i * g_j is divisible
          by k (since remaining factors of nums cancel with k/g).
        - Count frequencies of g = gcd(x,k); for each pair of gcd values check.

        Complexity: O(n * d(k) + d(k)^2) time, O(d(k)) space.
        """
        cnt = Counter(gcd(x, k) for x in nums)
        keys = list(cnt.keys())
        ans = 0
        for i, a in enumerate(keys):
            for b in keys[i:]:
                if (a * b) % k == 0:
                    if a == b:
                        ans += cnt[a] * (cnt[a] - 1) // 2
                    else:
                        ans += cnt[a] * cnt[b]
        return ans
# @lc code=end
