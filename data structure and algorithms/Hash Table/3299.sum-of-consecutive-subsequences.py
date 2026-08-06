#
# @lc app=leetcode id=3299 lang=python3
#
# [3299] Sum of Consecutive Subsequences
#
# https://leetcode.com/problems/sum-of-consecutive-subsequences/description/
#
# algorithms
# Hard (44.75%)
# Likes:    7
# Dislikes: 1
# Total Accepted:    584
# Total Submissions: 1.3K
# Testcase Example:  "[1,2]"
#
#
# We call an array arr of length n consecutive if one of the following
# holds:
#
# arr[i] - arr[i - 1] == 1 for all 1 <= i < n.
#
# arr[i] - arr[i - 1] == -1 for all 1 <= i < n.
#
# The value of an array is the sum of its elements.
#
# For example, [3, 4, 5] is a consecutive array of value 12 and [9, 8] is
# another of value 17. While [3, 4, 3] and [8, 6] are not consecutive.
#
# Given an array of integers nums, return the sum of the values of all
# consecutive non-empty subsequences.
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# Note that an array of length 1 is also considered consecutive.
#
# Example 1:
#
# Input: nums = [1,2]
#
# Output: 6
#
# Explanation:
#
# The consecutive subsequences are: [1], [2], [1, 2].
#
# Example 2:
#
# Input: nums = [1,4,2,3]
#
# Output: 31
#
# Explanation:
#
# The consecutive subsequences are: [1], [4], [2], [3], [1, 2], [2, 3],
# [4, 3], [1, 2, 3].
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def getSum(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Sum values of all consecutive subsequences (step always +1 or always -1),
        mod 10^9+7. Length-1 counts once.

        Algorithm:
        - Increasing DP: cnt[v]/sm[v] = #/sum of inc subsequences ending at v.
          On x: extend from x-1 (plus singleton [x]); accumulate into maps.
        - Decreasing DP symmetrically from x+1.
        - Answer = inc + dec - sum(nums) (singletons double-counted).

        Complexity: O(n) time, O(U) space for distinct values seen.
        """
        MOD = 10**9 + 7

        def calc(diff: int) -> int:
            cnt: dict = defaultdict(int)
            sm: dict = defaultdict(int)
            total = 0
            for x in nums:
                prev = x - diff
                c = (1 + cnt[prev]) % MOD
                s = (x + sm[prev] + cnt[prev] * x) % MOD
                total = (total + s) % MOD
                cnt[x] = (cnt[x] + c) % MOD
                sm[x] = (sm[x] + s) % MOD
            return total

        singles = sum(nums) % MOD
        return (calc(1) + calc(-1) - singles) % MOD
# @lc code=end
