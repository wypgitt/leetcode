#
# @lc app=leetcode id=3919 lang=python3
#
# [3919] Minimum Cost to Move Between Indices
#
# https://leetcode.com/problems/minimum-cost-to-move-between-indices/description/
#
# algorithms
# Medium (50.76%)
# Likes:    86
# Dislikes: 5
# Total Accepted:    16.1K
# Total Submissions: 31.8K
# Testcase Example:  "[-5,-2,3]\n[[0,2],[2,0],[1,2]]"
#
#
# You are given an integer array nums where nums is strictly increasing.
#
# For each index x, let closest(x) be the adjacent index y such that
# abs(nums[x] - nums[y]) is minimized. If both adjacent indices exist and
# give the same difference, choose the smaller index.
#
# From any index x, you can move in two ways:
#
# To any index y with cost abs(nums[x] - nums[y]), or
#
# To closest(x) with cost 1.
#
# You are also given a 2D integer array queries, where each queries[i] =
# [l_i, r_i].
#
# For each query, calculate the minimum total cost to move from index l_i
# to index r_i.
#
# Return an integer array ans, where ans[i] is the answer for the i^th
# query.
#
# The absolute difference between two values x and y is defined as abs(x -
# y).
#
# Example 1:
#
# Input: nums = [-5,-2,3], queries = [[0,2],[2,0],[1,2]]
#
# Output: [6,2,5]
#
# Explanation:​​​​​​​​​​​​​​​​​​​​
#
# The closest indices are [1, 0, 1] respectively.
#
# For [0, 2], the path 0 → 1 → 2 uses a closest move from index 0 to 1
# with cost 1 and a move from index 1 to 2 with cost |-2 - 3| = 5, giving
# total 1 + 5 = 6.
#
# For [2, 0], the path 2 → 1 → 0 uses two closest moves from index 2 to 1
# and from index 1 to 0, each with cost 1, giving total 2.
#
# For [1, 2], the direct move from index 1 to index 2 has cost |-2 - 3| =
# 5, which is optimal.
#
# Thus, ans = [6, 2, 5].
#
# Example 2:
#
# Input: nums = [0,2,3,9], queries = [[3,0],[1,2],[2,0]]
#
# Output: [4,1,3]
#
# Explanation:
#
# The closest indices are [1, 2, 1, 2] respectively.
#
# For [3, 0], the path 3 → 2 → 1 → 0 uses closest moves from index 3 to 2
# and from 2 to 1, each with cost 1, and a move from 1 to 0 with cost |2 -
# 0| = 2, giving total 1 + 1 + 2 = 4.
#
# For [1, 2], the closest move from index 1 to 2 has cost 1.
#
# For [2, 0], the path 2 → 1 → 0 uses a closest move from index 2 to 1
# with cost 1 and a move from 1 to 0 with cost |2 - 0| = 2, giving total 1
# + 2 = 3.
#
# Thus, ans = [4, 1, 3].
#
# Constraints:
#
# 2 <= nums.length <= 10^5
#
# -10^9 <= nums[i] <= 10^9
#
# nums is strictly increasing
#
# 1 <= queries.length <= 10^5
#
# queries[i] = [l_i, r_i]​​​​​​​
#
# 0 <= l_i, r_i < nums.length
#

# @lc code=start
from typing import List


class Solution:
    def minCost(self, nums: List[int], queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        On a sorted line, move by paying |nums[x]-nums[y]| or cost 1 to the
        nearest neighbor (closest). Answer min cost for many (l, r) queries.

        Algorithm:
        - For each adjacent edge, cost going right/left is 1 if that neighbor is
          closest(x), else the absolute gap.
        - Prefix sums of rightward / leftward edge costs answer each query in O(1).

        Complexity: O(n + q) time, O(n) space.
        """
        n = len(nums)

        right_prefix = [0] * n
        left_prefix = [0] * n

        for i in range(n - 1):
            gap = nums[i + 1] - nums[i]

            right_step = 1 if self._closest(nums, i) == i + 1 else gap
            left_step = 1 if self._closest(nums, i + 1) == i else gap

            right_prefix[i + 1] = right_prefix[i] + right_step
            left_prefix[i + 1] = left_prefix[i] + left_step

        answer = []
        for left, right in queries:
            if left < right:
                answer.append(right_prefix[right] - right_prefix[left])
            else:
                answer.append(left_prefix[left] - left_prefix[right])

        return answer

    def _closest(self, nums: List[int], index: int) -> int:
        n = len(nums)
        if index == 0:
            return 1
        if index == n - 1:
            return n - 2

        left_gap = nums[index] - nums[index - 1]
        right_gap = nums[index + 1] - nums[index]
        if left_gap <= right_gap:
            return index - 1
        return index + 1
# @lc code=end
