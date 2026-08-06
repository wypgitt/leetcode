#
# @lc app=leetcode id=3935 lang=python3
#
# [3935] Power Update After K-th Largest Insertion I
#
# https://leetcode.com/problems/power-update-after-k-th-largest-insertion-i/description/
#
# algorithms
# Medium (67.93%)
# Likes:    4
# Dislikes: 1
# Total Accepted:    305
# Total Submissions: 449
# Testcase Example:  "[2]\n4\n[[3,1],[1,2]]"
#
#
# You are given an integer array nums and an integer p.
#
# You are also given a 2D integer array queries, where each queries[i] =
# [val_i, k_i] and the difference between consecutive k_i values is always
# less than 10.
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
# 1 <= nums.length <= 2 × 10^4
#
# 1 <= nums[i] <= 10^6
#
# ​​​​​​​1 <= p <= 10^6
#
# 1 <= queries.length <= 2 × 10^4
#
# ^​​​​​​​1 <= val_i <= 10^6
#
# 1 <= k_i <= n + i + 1
#
# |k_i - k_i - 1| < 10 for i > 0
#

# @lc code=start

from sortedcontainers import SortedList


class Solution:
    def powerUpdate(self, nums: list[int], p: int, queries: list[list[int]]) -> list[int]:
        """
        Interview explanation:
        Same as the II variant, but consecutive k differ by < 10. A SortedList
        still handles inserts and k-th-largest queries cleanly.

        Algorithm:
        - Maintain SortedList; for each query insert val, take [-k], pow update.

        Alternate (two lists):
        - Keep left (smaller) / right (k largest) SortedLists and rebalance when
          k moves by at most 9 — same asymptotics, smaller constants on k shifts.

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

    def powerUpdate_two_lists(self, nums: list[int], p: int, queries: list[list[int]]) -> list[int]:
        """
        Interview explanation:
        Alternate: two SortedLists where right holds exactly the current k
        largest; rebalance after each insert (k changes slowly).

        Algorithm:
        - Insert into right then rebalance |right| to k; x = right[0].

        Complexity: O((n + q) log (n + q)) time, O(n + q) space.
        """
        MOD = 10**9 + 7
        left, right = SortedList(), SortedList(nums)
        ans = []
        for val, k in queries:
            right.add(val)
            left.add(right.pop(0))
            while len(right) < k:
                right.add(left.pop())
            while len(right) > k:
                left.add(right.pop(0))
            p = pow(p, right[0], MOD)
            ans.append(p)
        return ans
# @lc code=end
