#
# @lc app=leetcode id=3510 lang=python3
#
# [3510] Minimum Pair Removal to Sort Array II
#
# https://leetcode.com/problems/minimum-pair-removal-to-sort-array-ii/description/
#
# algorithms
# Hard (38.94%)
# Likes:    417
# Dislikes: 39
# Total Accepted:    67.2K
# Total Submissions: 172.6K
# Testcase Example:  "[5,2,3,1]"
#
#
# Given an array nums, you can perform the following operation any number
# of times:
#
# Select the adjacent pair with the minimum sum in nums. If multiple such
# pairs exist, choose the leftmost one.
#
# Replace the pair with their sum.
#
# Return the minimum number of operations needed to make the array
# non-decreasing.
#
# An array is said to be non-decreasing if each element is greater than or
# equal to its previous element (if it exists).
#
# Example 1:
#
# Input: nums = [5,2,3,1]
#
# Output: 2
#
# Explanation:
#
# The pair (3,1) has the minimum sum of 4. After replacement, nums =
# [5,2,4].
#
# The pair (2,4) has the minimum sum of 6. After replacement, nums =
# [5,6].
#
# The array nums became non-decreasing in two operations.
#
# Example 2:
#
# Input: nums = [1,2,2]
#
# Output: 0
#
# Explanation:
#
# The array nums is already sorted.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^9 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List
from sortedcontainers import SortedList


class Solution:
    def minimumPairRemoval(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Same merge rule as I, but n <= 1e5. Simulate with a linked list of indices
        and an ordered set of (adjacent sum, left index); track inversion count
        locally when neighbors change.

        Algorithm:
        - prev/next arrays; SortedList of pair sums.
        - While inversions > 0: merge min pair into left node, update neighbor
          pairs and inversion deltas.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(nums)
        vals = [int(x) for x in nums]
        inv = sum(vals[i] > vals[i + 1] for i in range(n - 1))
        nxt = [i + 1 for i in range(n)]
        prv = [i - 1 for i in range(n)]
        pairs = SortedList((vals[i] + vals[i + 1], i) for i in range(n - 1))
        ans = 0
        while inv > 0:
            ans += 1
            pair_sum, cur = pairs.pop(0)
            nxt_i = nxt[cur]
            prv_i = prv[cur]
            if prv_i >= 0:
                old = vals[prv_i] + vals[cur]
                new = vals[prv_i] + pair_sum
                pairs.remove((old, prv_i))
                pairs.add((new, prv_i))
                if vals[prv_i] > vals[cur]:
                    inv -= 1
                if vals[prv_i] > pair_sum:
                    inv += 1
            if vals[nxt_i] < vals[cur]:
                inv -= 1
            nn = nxt[nxt_i] if nxt_i < n else n
            if nn < n:
                old = vals[nxt_i] + vals[nn]
                new = pair_sum + vals[nn]
                pairs.remove((old, nxt_i))
                pairs.add((new, cur))
                if vals[nn] < vals[nxt_i]:
                    inv -= 1
                if vals[nn] < pair_sum:
                    inv += 1
                prv[nn] = cur
            nxt[cur] = nn
            vals[cur] = pair_sum
        return ans
# @lc code=end
