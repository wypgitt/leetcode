#
# @lc app=leetcode id=3695 lang=python3
#
# [3695] Maximize Alternating Sum Using Swaps
#
# https://leetcode.com/problems/maximize-alternating-sum-using-swaps/description/
#
# algorithms
# Hard (62.45%)
# Likes:    61
# Dislikes: 5
# Total Accepted:    9.7K
# Total Submissions: 15.6K
# Testcase Example:  "[1,2,3]\n[[0,2],[1,2]]"
#
#
# You are given an integer array nums.
#
# You want to maximize the alternating sum of nums, which is defined as
# the value obtained by adding elements at even indices and subtracting
# elements at odd indices. That is, nums[0] - nums[1] + nums[2] -
# nums[3]...
#
# You are also given a 2D integer array swaps where swaps[i] = [p_i, q_i].
# For each pair [p_i, q_i] in swaps, you are allowed to swap the elements
# at indices p_i and q_i. These swaps can be performed any number of times
# and in any order.
#
# Return the maximum possible alternating sum of nums.
#
# Example 1:
#
# Input: nums = [1,2,3], swaps = [[0,2],[1,2]]
#
# Output: 4
#
# Explanation:
#
# The maximum alternating sum is achieved when nums is [2, 1, 3] or [3, 1,
# 2]. As an example, you can obtain nums = [2, 1, 3] as follows.
#
# Swap nums[0] and nums[2]. nums is now [3, 2, 1].
#
# Swap nums[1] and nums[2]. nums is now [3, 1, 2].
#
# Swap nums[0] and nums[2]. nums is now [2, 1, 3].
#
# Example 2:
#
# Input: nums = [1,2,3], swaps = [[1,2]]
#
# Output: 2
#
# Explanation:
#
# The maximum alternating sum is achieved by not performing any swaps.
#
# Example 3:
#
# Input: nums = [1,1000000000,1,1000000000,1,1000000000], swaps = []
#
# Output: -2999999997
#
# Explanation:
#
# Since we cannot perform any swaps, the maximum alternating sum is
# achieved by not performing any swaps.
#
# Constraints:
#
# 2 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# 0 <= swaps.length <= 10^5
#
# swaps[i] = [p_i, q_i]
#
# 0 <= p_i < q_i <= nums.length - 1
#
# [p_i, q_i] != [p_j, q_j]
#

# @lc code=start

from typing import List


class Solution:
    def maxAlternatingSum(self, nums: List[int], swaps: List[List[int]]) -> int:
        """
        Interview explanation:
        Allowed swaps form an undirected graph; values can be freely reassigned
        inside each connected component. Alternating sum adds even indices and
        subtracts odd ones, so put the largest values on even slots.

        Algorithm:
        - Union-Find on swap edges.
        - Per component: collect values and even-index count; sort values
          descending, add the top even_count, subtract the rest.

        Complexity: O(n + m + n log n) time, O(n) space.
        """
        n = len(nums)
        parent = list(range(n))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra

        for p, q in swaps:
            union(p, q)

        vals: dict[int, list[int]] = {}
        even_cnt: dict[int, int] = {}
        for i, x in enumerate(nums):
            r = find(i)
            vals.setdefault(r, []).append(x)
            if i % 2 == 0:
                even_cnt[r] = even_cnt.get(r, 0) + 1
            else:
                even_cnt.setdefault(r, 0)

        ans = 0
        for r, arr in vals.items():
            arr.sort(reverse=True)
            e = even_cnt[r]
            for i, v in enumerate(arr):
                ans += v if i < e else -v
        return ans
# @lc code=end
