#
# @lc app=leetcode id=3636 lang=python3
#
# [3636] Threshold Majority Queries
#
# https://leetcode.com/problems/threshold-majority-queries/description/
#
# algorithms
# Hard (21.99%)
# Likes:    46
# Dislikes: 10
# Total Accepted:    5K
# Total Submissions: 22.8K
# Testcase Example:  "[1,1,2,2,1,1]\n[[0,5,4],[0,3,3],[2,3,2]]"
#
#
# You are given an integer array nums of length n and an array queries,
# where queries[i] = [l_i, r_i, threshold_i].
#
# Return an array of integers ans where ans[i] is equal to the element in
# the subarray nums[l_i...r_i] that appears at least threshold_i times,
# selecting the element with the highest frequency (choosing the smallest
# in case of a tie), or -1 if no such element exists.
#
# Example 1:
#
# Input: nums = [1,1,2,2,1,1], queries = [[0,5,4],[0,3,3],[2,3,2]]
#
# Output: [1,-1,2]
#
# Explanation:
#
#                         Query
#                         Sub-array
#                         Threshold
#                         Frequency table
#                         Answer
#
#                         [0, 5, 4]
#                         [1, 1, 2, 2, 1, 1]
#                         4
#                         1 → 4, 2 → 2
#                         1
#
#                         [0, 3, 3]
#                         [1, 1, 2, 2]
#                         3
#                         1 → 2, 2 → 2
#                         -1
#
#                         [2, 3, 2]
#                         [2, 2]
#                         2
#                         2 → 2
#                         2
#
# Example 2:
#
# Input: nums = [3,2,3,2,3,2,3], queries =
# [[0,6,4],[1,5,2],[2,4,1],[3,3,1]]
#
# Output: [3,2,3,2]
#
# Explanation:
#
#                         Query
#                         Sub-array
#                         Threshold
#                         Frequency table
#                         Answer
#
#                         [0, 6, 4]
#                         [3, 2, 3, 2, 3, 2, 3]
#                         4
#                         3 → 4, 2 → 3
#                         3
#
#                         [1, 5, 2]
#                         [2, 3, 2, 3, 2]
#                         2
#                         2 → 3, 3 → 2
#                         2
#
#                         [2, 4, 1]
#                         [3, 2, 3]
#                         1
#                         3 → 2, 2 → 1
#                         3
#
#                         [3, 3, 1]
#                         [2]
#                         1
#                         2 → 1
#                         2
#
# Constraints:
#
# 1 <= nums.length == n <= 10^4
#
# 1 <= nums[i] <= 10^9
#
# 1 <= queries.length <= 5 * 10^4
#
# queries[i] = [l_i, r_i, threshold_i]
#
# 0 <= l_i <= r_i < n
#
# 1 <= threshold_i <= r_i - l_i + 1
#

# @lc code=start

from typing import List


class Solution:
    def subarrayMajority(self, nums: List[int], queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Offline range queries: among values with frequency >= threshold, pick
        the one with highest frequency (smallest value on ties), else -1.
        Mo's algorithm maintains the current subarray; a segment tree on
        compressed values tracks (max_freq, min_value).

        Algorithm:
        - Compress values; segment tree leaf i stores (freq, value).
        - Sort queries in Mo order; add/remove update the tree.
        - Answer is tree-root value if freq >= threshold else -1.

        Complexity: O((n+q) sqrt(n) log n) time, O(n+q) space.
        """
        sorted_vals = sorted(set(nums))
        index = {v: i for i, v in enumerate(sorted_vals)}
        m = len(sorted_vals)
        size = 1
        while size < m:
            size *= 2
        tree = [(0, float("inf"))] * (2 * size)
        freq = [0] * m

        def merge(a, b):
            if a[0] > b[0]:
                return a
            if b[0] > a[0]:
                return b
            return (a[0], min(a[1], b[1]))

        def update(i: int, delta: int) -> None:
            freq[i] += delta
            j = i + size
            tree[j] = (freq[i], sorted_vals[i] if freq[i] > 0 else float("inf"))
            j //= 2
            while j:
                tree[j] = merge(tree[2 * j], tree[2 * j + 1])
                j //= 2

        def add(i: int) -> None:
            update(index[nums[i]], 1)

        def remove(i: int) -> None:
            update(index[nums[i]], -1)

        block = int(len(nums) ** 0.5) + 1
        order = sorted(
            range(len(queries)),
            key=lambda i: (
                queries[i][0] // block,
                queries[i][1] if (queries[i][0] // block) & 1 else -queries[i][1],
            ),
        )
        ans = [-1] * len(queries)
        left, right = 0, -1
        for qi in order:
            l, r, t = queries[qi]
            while left > l:
                left -= 1
                add(left)
            while right < r:
                right += 1
                add(right)
            while left < l:
                remove(left)
                left += 1
            while right > r:
                remove(right)
                right -= 1
            f, v = tree[1]
            ans[qi] = int(v) if f >= t else -1
        return ans
# @lc code=end

