#
# @lc app=leetcode id=3526 lang=python3
#
# [3526] Range XOR Queries with Subarray Reversals
#
# https://leetcode.com/problems/range-xor-queries-with-subarray-reversals/description/
#
# algorithms
# Hard (62.70%)
# Likes:    3
# Dislikes: 2
# Total Accepted:    442
# Total Submissions: 705
# Testcase Example:  "[1,2,3,4,5]\n[[2,1,3],[1,2,10],[3,0,4],[2,0,4]]"
#
#
# You are given an integer array nums of length n and a 2D integer array
# queries of length q, where each query is one of the following three
# types:
#
# Update: queries[i] = [1, index, value]
#
#         Set nums[index] = value.
#
# Range XOR Query: queries[i] = [2, left, right]
#
#         Compute the bitwise XOR of all elements in the subarray
# nums[left...right], and record this result.
#
# Reverse Subarray: queries[i] = [3, left, right]
#
#         Reverse the subarray nums[left...right] in place.
#
# Return an array of the results of all range XOR queries in the order
# they were encountered.
#
# Example 1:
#
# Input: nums = [1,2,3,4,5], queries = [[2,1,3],[1,2,10],[3,0,4],[2,0,4]]
#
# Output: [5,8]
#
# Explanation:
#
# Query 1: [2, 1, 3] – Compute XOR of subarray [2, 3, 4] resulting in 5.
#
# Query 2: [1, 2, 10] – Update nums[2] to 10, updating the array to [1, 2,
# 10, 4, 5].
#
# Query 3: [3, 0, 4] – Reverse the entire array to get [5, 4, 10, 2, 1].
#
# Query 4: [2, 0, 4] – Compute XOR of subarray [5, 4, 10, 2, 1] resulting
# in 8.
#
# Example 2:
#
# Input: nums = [7,8,9], queries = [[1,0,3],[2,0,2],[3,1,2]]
#
# Output: [2]
#
# Explanation:
#
# Query 1: [1, 0, 3] – Update nums[0] to 3, updating the array to [3, 8,
# 9].
#
# Query 2: [2, 0, 2] – Compute XOR of subarray [3, 8, 9] resulting in 2.
#
# Query 3: [3, 1, 2] – Reverse the subarray [8, 9] to get [9, 8].
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 0 <= nums[i] <= 10^9
#
# 1 <= queries.length <= 10^5
#
# queries[i].length == 3​
#
# queries[i][0] ∈ {1, 2, 3}​
#
# If queries[i][0] == 1:​
#
# 0 <= index < nums.length​
#
# 0 <= value <= 10^9
#
# If queries[i][0] == 2 or queries[i][0] == 3:​
#
# 0 <= left <= right < nums.length​
#

# @lc code=start
from typing import List


class Solution:
    def getResults(self, nums: List[int], queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        XOR is commutative and associative, so reversing a subarray never changes
        any range XOR. Only point updates and range XOR queries matter.

        Algorithm:
        - Fenwick / BIT storing prefix XORs for point set and range XOR.
        - Ignore type-3 reverse operations.

        Complexity: O((n + q) log n) time, O(n) space.
        """
        n = len(nums)
        bit = [0] * (n + 1)
        arr = nums[:]

        def fenw_update(i: int, delta: int) -> None:
            i += 1
            while i <= n:
                bit[i] ^= delta
                i += i & -i

        def fenw_prefix(i: int) -> int:
            i += 1
            res = 0
            while i > 0:
                res ^= bit[i]
                i -= i & -i
            return res

        def range_xor(left: int, right: int) -> int:
            return fenw_prefix(right) ^ (fenw_prefix(left - 1) if left else 0)

        for i, v in enumerate(arr):
            fenw_update(i, v)

        ans: List[int] = []
        for typ, a, b in queries:
            if typ == 1:
                fenw_update(a, arr[a] ^ b)
                arr[a] = b
            elif typ == 2:
                ans.append(range_xor(a, b))
            # typ == 3: reverse is a no-op for XOR
        return ans

    def getResults_segtree(self, nums: List[int], queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Alternate: segment tree for point update / range XOR; reverse ignored.

        Algorithm:
        - Classic XOR segment tree over the array.

        Complexity: O((n + q) log n) time, O(n) space.
        """
        n = len(nums)
        tree = [0] * (4 * n)

        def build(idx: int, lo: int, hi: int) -> None:
            if lo == hi:
                tree[idx] = nums[lo]
                return
            mid = (lo + hi) // 2
            build(idx * 2, lo, mid)
            build(idx * 2 + 1, mid + 1, hi)
            tree[idx] = tree[idx * 2] ^ tree[idx * 2 + 1]

        def update(idx: int, lo: int, hi: int, pos: int, val: int) -> None:
            if lo == hi:
                tree[idx] = val
                return
            mid = (lo + hi) // 2
            if pos <= mid:
                update(idx * 2, lo, mid, pos, val)
            else:
                update(idx * 2 + 1, mid + 1, hi, pos, val)
            tree[idx] = tree[idx * 2] ^ tree[idx * 2 + 1]

        def query(idx: int, lo: int, hi: int, L: int, R: int) -> int:
            if R < lo or hi < L:
                return 0
            if L <= lo and hi <= R:
                return tree[idx]
            mid = (lo + hi) // 2
            return query(idx * 2, lo, mid, L, R) ^ query(
                idx * 2 + 1, mid + 1, hi, L, R
            )

        build(1, 0, n - 1)
        ans: List[int] = []
        for typ, a, b in queries:
            if typ == 1:
                update(1, 0, n - 1, a, b)
            elif typ == 2:
                ans.append(query(1, 0, n - 1, a, b))
        return ans
# @lc code=end
