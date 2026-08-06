#
# @lc app=leetcode id=3762 lang=python3
#
# [3762] Minimum Operations to Equalize Subarrays
#
# https://leetcode.com/problems/minimum-operations-to-equalize-subarrays/description/
#
# algorithms
# Hard (20.98%)
# Likes:    51
# Dislikes: 3
# Total Accepted:    3.4K
# Total Submissions: 16.2K
# Testcase Example:  "[1,4,7]\n3\n[[0,1],[0,2]]"
#
#
# You are given an integer array nums and an integer k.
#
# In one operation, you can increase or decrease any element of nums by
# exactly k.
#
# You are also given a 2D integer array queries, where each queries[i] =
# [l_i, r_i].
#
# For each query, find the minimum number of operations required to make
# all elements in the subarray nums[l_i..r_i] equal. If it is impossible,
# the answer for that query is -1.
#
# Return an array ans, where ans[i] is the answer for the i^th query.
#
# Example 1:
#
# Input: nums = [1,4,7], k = 3, queries = [[0,1],[0,2]]
#
# Output: [1,2]
#
# Explanation:
#
# One optimal set of operations:
#
#                         i
#                         [l_i, r_i]
#                         nums[l_i..r_i]
#                         Possibility
#                         Operations
#                         Final
#
#                         nums[l_i..r_i]
#                         ans[i]
#
#                         0
#                         [0, 1]
#                         [1, 4]
#                         Yes
#                         nums[0] + k = 1 + 3 = 4 = nums[1]
#                         [4, 4]
#                         1
#
#                         1
#                         [0, 2]
#                         [1, 4, 7]
#                         Yes
#                         nums[0] + k = 1 + 3 = 4 = nums[1]
#
#                         nums[2] - k = 7 - 3 = 4 = nums[1]
#                         [4, 4, 4]
#                         2
#
# Thus, ans = [1, 2].
#
# Example 2:
#
# Input: nums = [1,2,4], k = 2, queries = [[0,2],[0,0],[1,2]]
#
# Output: [-1,0,1]
#
# Explanation:
#
# One optimal set of operations:
#
#                         i
#                         [l_i, r_i]
#                         nums[l_i..r_i]
#                         Possibility
#                         Operations
#                         Final
#
#                         nums[l_i..r_i]
#                         ans[i]
#
#                         0
#                         [0, 2]
#                         [1, 2, 4]
#                         No
#                         -
#                         [1, 2, 4]
#                         -1
#
#                         1
#                         [0, 0]
#                         [1]
#                         Yes
#                         Already equal
#                         [1]
#                         0
#
#                         2
#                         [1, 2]
#                         [2, 4]
#                         Yes
#                         nums[1] + k = 2 + 2 = 4 = nums[2]
#                         [4, 4]
#                         1
#
# Thus, ans = [-1, 0, 1].
#
# Constraints:
#
# 1 <= n == nums.length <= 4 × 10^4
#
# 1 <= nums[i] <= 10^9​​​​​​​
#
# 1 <= k <= 10^9
#
# 1 <= queries.length <= 4 × 10^4
#
# ^​​​​​​​queries[i] = [l_i, r_i]
#
# 0 <= l_i <= r_i <= n - 1
#

# @lc code=start
from typing import List


class PersistentSegmentTree:
    """Persistent fenwick-like segment tree for range median L1 cost."""

    __slots__ = ("vals", "idx", "n", "roots")

    def __init__(self, arr: List[int]):
        self.vals = sorted(set(arr))
        self.idx = {v: i for i, v in enumerate(self.vals)}
        self.n = len(self.vals)
        self.roots: List[list] = []
        self._build(arr)

    def _node(self):
        # [left, right, count, total]
        return [None, None, 0, 0]

    def _build(self, arr: List[int]):
        root = self._node()
        self.roots.append(root)
        for x in arr:
            root = root[:]
            self.roots.append(root)
            cur = root
            left, right = 0, self.n - 1
            i = self.idx[x]
            while left < right:
                cur[2] += 1
                cur[3] += x
                mid = (left + right) // 2
                if i <= mid:
                    cur[0] = (cur[0][:] if cur[0] else self._node())
                    cur = cur[0]
                    right = mid
                else:
                    cur[1] = (cur[1][:] if cur[1] else self._node())
                    cur = cur[1]
                    left = mid + 1
            cur[2] += 1
            cur[3] += x

    def query(self, l: int, r: int) -> int:
        """
        Interview explanation:
        Persistent fenwick/segtree range query: L1 cost to bring values on [l,r]
        to their median (in compressed value space).

        Algorithm:
        - Walk two version roots to find median; accumulate left/right L1.

        Complexity: O(log V) time per query.
        """
        a, b = self.roots[l], self.roots[r + 1]
        left_cnt = left_total = 0
        need = (r - l + 1) // 2 + 1
        left, right = 0, self.n - 1
        while left < right:
            mid = (left + right) // 2
            cnt = ((b[0][2] if b and b[0] else 0) - (a[0][2] if a and a[0] else 0))
            if need <= cnt:
                a = a[0] if a else None
                b = b[0] if b else None
                right = mid
            else:
                need -= cnt
                left_cnt += cnt
                left_total += ((b[0][3] if b and b[0] else 0) - (a[0][3] if a and a[0] else 0))
                a = a[1] if a else None
                b = b[1] if b else None
                left = mid + 1
        med = self.vals[left]
        total = self.roots[r + 1][3] - self.roots[l][3]
        return (med * left_cnt - left_total) + (
            (total - left_total) - med * ((r - l + 1) - left_cnt)
        )


class Solution:
    def minOperations(self, nums: List[int], k: int, queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        ±k preserves residue mod k, so a range is feasible iff all share the same
        residue. Values nums[i]//k must meet at their median; cost is L1 to that median.

        Algorithm:
        - Prefix-mark residue changes to test feasibility in O(1).
        - Persistent segment tree over nums[i]//k answers range sum |x - median|.

        Complexity: O((n + q) log n) time, O(n log n) space.
        """
        n = len(nums)
        pref = [0] * (n + 1)
        for i in range(n):
            pref[i + 1] = pref[i] + (
                1 if i >= 1 and nums[i] % k != nums[i - 1] % k else 0
            )
        pst = PersistentSegmentTree([x // k for x in nums])
        ans = []
        for l, r in queries:
            if pref[r + 1] - pref[l + 1] != 0:
                ans.append(-1)
            else:
                ans.append(pst.query(l, r))
        return ans

    def minOperations_sort_each(self, nums: List[int], k: int, queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Alternate: answer each query by sorting the compressed values (slower).

        Algorithm:
        - If residues differ, -1; else L1 distance of nums[i]//k to their median.

        Complexity: O(q * m log m) time per range length m, O(m) space.
        """
        ans = []
        for l, r in queries:
            seg = nums[l : r + 1]
            if any(x % k != seg[0] % k for x in seg):
                ans.append(-1)
                continue
            a = sorted(x // k for x in seg)
            med = a[len(a) // 2]
            ans.append(sum(abs(x - med) for x in a))
        return ans
# @lc code=end
