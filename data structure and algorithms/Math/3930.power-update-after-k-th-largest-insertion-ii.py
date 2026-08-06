#
# @lc app=leetcode id=3930 lang=python3
#
# [3930] Power Update After K-th Largest Insertion II
#
# https://leetcode.com/problems/power-update-after-k-th-largest-insertion-ii/description/
#
# algorithms
# Hard (81.49%)
# Likes:    2
# Dislikes: 1
# Total Accepted:    471
# Total Submissions: 578
# Testcase Example:  "[2]\n4\n[[3,1],[1,2]]"
#
#
# You are given an integer array nums and an integer p.
#
# You are also given a 2D integer array queries, where each queries[i] =
# [val_i, k_i].
#
# For each query:
#
# Insert val_i into nums.
#
# Let x be the k_i^th largest element in the current nums.
#
# Update p to p^x % (10^9 + 7).
#
# Return an array ans where the ans[i] represents the value of p after
# processing the i^th query.
#
# Example 1:
#
# Input: nums = [2], p = 4, queries = [[3,1],[1,2]]
#
# Output: [64,4096]
#
# Explanation:
#
#                         i
#                         val_i
#                         Current
#
#                         nums
#                         k_i
#                         k_i^th
#
#                         largest
#                         p
#                         New p = p^k % (10^9 + 7)
#
#                         0
#                         3
#                         [2, 3]
#                         1
#                         3
#                         4
#                         4^3 % (10^9 + 7) = 64
#
#                         1
#                         1
#                         [2, 3, 1]
#                         2
#                         2
#                         64
#                         64^2 % (10^9 + 7) = 4096
#
# Thus, ans = [64, 4096].
#
# Example 2:
#
# Input: nums = [7,5], p = 6, queries = [[4,3],[7,2]]
#
# Output: [1296,220296870]
#
# Explanation:
#
#                         i
#                         val_i
#                         Current​​​​​​​
#
#                         nums
#                         k_i
#                         k_i^th
#
#                         largest
#                         p
#                         New p = p^k % (10^9 + 7)
#
#                         0
#                         4
#                         [7, 5, 4]
#                         3
#                         4
#                         6
#                         6^4 % (10^9 + 7) = 1296
#
#                         1
#                         7
#                         [7, 5, 4, 7]
#                         2
#                         7
#                         1296
#                         1296^7 % (10^9 + 7) = 220296870
#
# Thus, ans = [1296, 220296870]
#
# Constraints:
#
# 1 <= nums.length <= 2 * 10^4
#
# 1 <= nums[i] <= 10^9
#
# ​​​​​​​1 <= p <= 10^9
#
# 1 <= queries.length <= 2 * 10^4
#
# ^​​​​​​​1 <= val_i <= 10^9
#
# 1 <= k_i <= n + i + 1​​​​​​​
#

# @lc code=start

from sortedcontainers import SortedList


class Solution:
    def powerUpdate(self, nums: list[int], p: int, queries: list[list[int]]) -> list[int]:
        """
        Interview explanation:
        After each insertion, raise p to the k-th largest element modulo 1e9+7.
        Maintain a sorted multiset for O(log n) insert and k-th largest lookup.

        Algorithm:
        - SortedList of current values.
        - For each [val, k]: insert val; x = sorted[-k]; p = pow(p, x, MOD).

        Complexity: O((n + q) log (n + q)) time, O(n + q) space.
        """
        MOD = 10**9 + 7
        sl = SortedList(nums)
        ans = []
        for val, k in queries:
            sl.add(val)
            p = pow(p, sl[-k], MOD)
            ans.append(p)
        return ans
# @lc code=end
