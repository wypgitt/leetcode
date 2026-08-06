#
# @lc app=leetcode id=2834 lang=python3
#
# [2834] Find the Minimum Possible Sum of a Beautiful Array
#
# https://leetcode.com/problems/find-the-minimum-possible-sum-of-a-beautiful-array/description/
#
# algorithms
# Medium (34.66%)
# Likes:    321
# Dislikes: 59
# Total Accepted:    33.6K
# Total Submissions: 96.9K
# Testcase Example:  "2\n3"
#
#
# You are given positive integers n and target.
#
# An array nums is beautiful if it meets the following conditions:
#
# nums.length == n.
#
# nums consists of pairwise distinct positive integers.
#
# There doesn't exist two distinct indices, i and j, in the range [0, n -
# 1], such that nums[i] + nums[j] == target.
#
# Return the minimum possible sum that a beautiful array could have modulo
# 10^9 + 7.
#
# Example 1:
#
# Input: n = 2, target = 3
# Output: 4
# Explanation: We can see that nums = [1,3] is beautiful.
# - The array nums has length n = 2.
# - The array nums consists of pairwise distinct positive integers.
# - There doesn't exist two distinct indices, i and j, with nums[i] +
# nums[j] == 3.
# It can be proven that 4 is the minimum possible sum that a beautiful
# array could have.
#
# Example 2:
#
# Input: n = 3, target = 3
# Output: 8
# Explanation: We can see that nums = [1,3,4] is beautiful.
# - The array nums has length n = 3.
# - The array nums consists of pairwise distinct positive integers.
# - There doesn't exist two distinct indices, i and j, with nums[i] +
# nums[j] == 3.
# It can be proven that 8 is the minimum possible sum that a beautiful
# array could have.
#
# Example 3:
#
# Input: n = 1, target = 1
# Output: 1
# Explanation: We can see, that nums = [1] is beautiful.
#
# Constraints:
#
# 1 <= n <= 10^9
#
# 1 <= target <= 10^9
#

# @lc code=start
class Solution:
    def minimumPossibleSum(self, n: int, target: int) -> int:
        """
        Interview explanation:
        Same structure as k-avoiding arrays: distinct positives, no pair sums to
        target; minimize sum mod 10^9+7. n can be 1e9 so use O(1) arithmetic.

        Algorithm:
        - Take 1..m with m=target//2 (pairs summing to target start at >= target).
        - If need more, take target, target+1, ... .
        - Sum with triangular formulas; mod 10^9+7.

        Complexity: O(1) time, O(1) space.
        """
        MOD = 10**9 + 7
        m = target // 2
        if n <= m:
            return (n * (n + 1) // 2) % MOD
        first = m * (m + 1) // 2
        rem = n - m
        second = rem * (2 * target + rem - 1) // 2
        return (first + second) % MOD
# @lc code=end
