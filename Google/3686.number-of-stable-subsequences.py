#
# @lc app=leetcode id=3686 lang=python3
#
# [3686] Number of Stable Subsequences
#
# https://leetcode.com/problems/number-of-stable-subsequences/description/
#
# algorithms
# Hard (60.19%)
# Likes:    92
# Dislikes: 3
# Total Accepted:    25.2K
# Total Submissions: 41.8K
# Testcase Example:  "[1,3,5]"
#
#
# You are given an integer array nums.
#
# A subsequence is stable if it does not contain three consecutive
# elements with the same parity when the subsequence is read in order
# (i.e., consecutive inside the subsequence).
#
# Return the number of stable subsequences.
#
# Since the answer may be too large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: nums = [1,3,5]
#
# Output: 6
#
# Explanation:
#
# Stable subsequences are [1], [3], [5], [1, 3], [1, 5], and [3, 5].
#
# Subsequence [1, 3, 5] is not stable because it contains three
# consecutive odd numbers. Thus, the answer is 6.
#
# Example 2:
#
# Input: nums = [2,3,4,2]
#
# Output: 14
#
# Explanation:
#
# The only subsequence that is not stable is [2, 4, 2], which contains
# three consecutive even numbers.
#
# All other subsequences are stable. Thus, the answer is 14.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^​​​​​​​5
#

# @lc code=start

from typing import List


class Solution:
    def countStableSubsequences(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Stability forbids three same-parity ends in a row. Track how many
        stable subsequences end with one or two consecutive odds/evens.

        Algorithm:
        - States: o1, o2, e1, e2 (ending odd/even streak length 1 or 2).
        - On odd x: new o1 from any even-ending (or alone); new o2 from o1.
        - On even x: symmetric. Accumulate into states mod 10^9+7.

        Complexity: O(n) time, O(1) space.
        """
        MOD = 10**9 + 7
        o1 = o2 = e1 = e2 = 0
        for x in nums:
            if x & 1:
                no1 = (e1 + e2 + 1) % MOD
                no2 = o1
                o1 = (o1 + no1) % MOD
                o2 = (o2 + no2) % MOD
            else:
                ne1 = (o1 + o2 + 1) % MOD
                ne2 = e1
                e1 = (e1 + ne1) % MOD
                e2 = (e2 + ne2) % MOD
        return (o1 + o2 + e1 + e2) % MOD
# @lc code=end
