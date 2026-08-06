#
# @lc app=leetcode id=3410 lang=python3
#
# [3410] Maximize Subarray Sum After Removing All Occurrences of One Element
#
# https://leetcode.com/problems/maximize-subarray-sum-after-removing-all-occurrences-of-one-element/description/
#
# algorithms
# Hard (23.56%)
# Likes:    67
# Dislikes: 6
# Total Accepted:    4.4K
# Total Submissions: 18.9K
# Testcase Example:  "[-3,2,-2,-1,3,-2,3]"
#
#
# You are given an integer array nums.
#
# You can do the following operation on the array at most once:
#
# Choose any integer x such that nums remains non-empty on removing all
# occurrences of x.
#
# Remove all occurrences of x from the array.
#
# Return the maximum subarray sum across all possible resulting arrays.
#
# Example 1:
#
# Input: nums = [-3,2,-2,-1,3,-2,3]
#
# Output: 7
#
# Explanation:
#
# We can have the following arrays after at most one operation:
#
# The original array is nums = [-3, 2, -2, -1, 3, -2, 3]. The maximum
# subarray sum is 3 + (-2) + 3 = 4.
#
# Deleting all occurences of x = -3 results in nums = [2, -2, -1, 3, -2,
# 3]. The maximum subarray sum is 3 + (-2) + 3 = 4.
#
# Deleting all occurences of x = -2 results in nums = [-3, 2, -1, 3, 3].
# The maximum subarray sum is 2 + (-1) + 3 + 3 = 7.
#
# Deleting all occurences of x = -1 results in nums = [-3, 2, -2, 3, -2,
# 3]. The maximum subarray sum is 3 + (-2) + 3 = 4.
#
# Deleting all occurences of x = 3 results in nums = [-3, 2, -2, -1, -2].
# The maximum subarray sum is 2.
#
# The output is max(4, 4, 7, 4, 2) = 7.
#
# Example 2:
#
# Input: nums = [1,2,3,4]
#
# Output: 10
#
# Explanation:
#
# It is optimal to not perform any operations.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^6 <= nums[i] <= 10^6
#

# @lc code=start
from typing import Dict, List


class Solution:
    def maxSubarraySum(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Optionally delete all occurrences of one value, then take max
        subarray sum. Removing positives never helps, so only consider
        deleting a negative value (or deleting nothing). Extend Kadane
        with a modified min-prefix that accounts for one deleted value.

        Algorithm:
        - Track prefix, plain minPrefix, and modifiedMinPrefix after
          optionally removing one negative value's contribution.
        - For each negative x, maintain min prefix-plus-removed-x.
        - ans = max(prefix - modifiedMinPrefix).

        Complexity: O(n) time, O(U) space for distinct negatives.
        """
        ans = max(nums)
        prefix = 0
        min_prefix = 0
        modified_min_prefix = 0
        count: Dict[int, int] = {}
        min_prefix_plus_removal: Dict[int, int] = {}

        for num in nums:
            prefix += num
            ans = max(ans, prefix - modified_min_prefix)
            if num < 0:
                count[num] = count.get(num, 0) + 1
                min_prefix_plus_removal[num] = (
                    min(min_prefix_plus_removal.get(num, 0), min_prefix) + num
                )
                modified_min_prefix = min(
                    modified_min_prefix,
                    count[num] * num,
                    min_prefix_plus_removal[num],
                )
            min_prefix = min(min_prefix, prefix)
            modified_min_prefix = min(modified_min_prefix, min_prefix)

        return ans

    def maxSubarraySum_segmentTree(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Classic alternative: segment tree storing sum/prefix/suffix/best.
        For each distinct value, set its positions to 0 (bridging gaps)
        and query global max subarray; restore afterwards.

        Algorithm:
        - Build segment tree; baseline from all-positive / all-negative
          shortcuts; try zeroing each value's indices.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(nums)
        if all(x >= 0 for x in nums):
            return sum(nums)
        mx = max(nums)
        if mx < 0:
            return mx

        class Node:
            __slots__ = ("sum", "pref", "suff", "best")

            def __init__(self, v: int = 0):
                self.sum = self.pref = self.suff = self.best = v

        def merge(a: Node, b: Node) -> Node:
            c = Node()
            c.sum = a.sum + b.sum
            c.pref = max(a.pref, a.sum + b.pref)
            c.suff = max(b.suff, b.sum + a.suff)
            c.best = max(a.best, b.best, a.suff + b.pref)
            return c

        tree = [Node() for _ in range(4 * n)]

        def build(idx: int, l: int, r: int) -> None:
            if l == r:
                tree[idx] = Node(nums[l])
                return
            m = (l + r) // 2
            build(idx * 2, l, m)
            build(idx * 2 + 1, m + 1, r)
            tree[idx] = merge(tree[idx * 2], tree[idx * 2 + 1])

        def update(idx: int, l: int, r: int, pos: int, val: int) -> None:
            if l == r:
                tree[idx] = Node(val)
                return
            m = (l + r) // 2
            if pos <= m:
                update(idx * 2, l, m, pos, val)
            else:
                update(idx * 2 + 1, m + 1, r, pos, val)
            tree[idx] = merge(tree[idx * 2], tree[idx * 2 + 1])

        build(1, 0, n - 1)
        positions: Dict[int, List[int]] = {}
        for i, v in enumerate(nums):
            positions.setdefault(v, []).append(i)

        ans = tree[1].best
        for v, idxs in positions.items():
            for i in idxs:
                update(1, 0, n - 1, i, 0)
            ans = max(ans, tree[1].best)
            for i in idxs:
                update(1, 0, n - 1, i, v)
        return ans
# @lc code=end
