#
# @lc app=leetcode id=3569 lang=python3
#
# [3569] Maximize Count of Distinct Primes After Split
#
# https://leetcode.com/problems/maximize-count-of-distinct-primes-after-split/description/
#
# algorithms
# Hard (19.34%)
# Likes:    27
# Dislikes: 7
# Total Accepted:    3.1K
# Total Submissions: 15.9K
# Testcase Example:  "[2,1,3,1,2]\n[[1,2],[3,3]]"
#
#
# You are given an integer array nums having length n and a 2D integer
# array queries where queries[i] = [idx, val].
#
# For each query:
#
# Update nums[idx] = val.
#
# Choose an integer k with 1 <= k < n to split the array into the
# non-empty prefix nums[0..k-1] and suffix nums[k..n-1] such that the sum
# of the counts of distinct prime values in each part is maximum.
#
# Note: The changes made to the array in one query persist into the next
# query.
#
# Return an array containing the result for each query, in the order they
# are given.
#
# Example 1:
#
# Input: nums = [2,1,3,1,2], queries = [[1,2],[3,3]]
#
# Output: [3,4]
#
# Explanation:
#
# Initially nums = [2, 1, 3, 1, 2].
#
# After 1^st query, nums = [2, 2, 3, 1, 2]. Split nums into [2] and [2, 3,
# 1, 2]. [2] consists of 1 distinct prime and [2, 3, 1, 2] consists of 2
# distinct primes. Hence, the answer for this query is 1 + 2 = 3.
#
# After 2^nd query, nums = [2, 2, 3, 3, 2]. Split nums into [2, 2, 3] and
# [3, 2] with an answer of 2 + 2 = 4.
#
# The output is [3, 4].
#
# Example 2:
#
# Input: nums = [2,1,4], queries = [[0,1]]
#
# Output: [0]
#
# Explanation:
#
# Initially nums = [2, 1, 4].
#
# After 1^st query, nums = [1, 1, 4]. There are no prime numbers in nums,
# hence the answer for this query is 0.
#
# The output is [0].
#
# Constraints:
#
# 2 <= n == nums.length <= 5 * 10^4
#
# 1 <= queries.length <= 5 * 10^4
#
# 1 <= nums[i] <= 10^5
#
# 0 <= queries[i][0] < nums.length
#
# 1 <= queries[i][1] <= 10^5
#

# @lc code=start

from typing import List
import heapq


class _SegTree:
    def __init__(self, n: int):
        self.n = n
        size = 1
        while size < n:
            size <<= 1
        self.size = size
        self.mx = [0] * (2 * size)
        self.lazy = [0] * (2 * size)

    def _apply(self, idx: int, val: int) -> None:
        self.mx[idx] += val
        self.lazy[idx] += val

    def _push(self, idx: int) -> None:
        if self.lazy[idx]:
            self._apply(idx * 2, self.lazy[idx])
            self._apply(idx * 2 + 1, self.lazy[idx])
            self.lazy[idx] = 0

    def _update(self, l: int, r: int, val: int, idx: int, nl: int, nr: int) -> None:
        if l > nr or r < nl:
            return
        if l <= nl and nr <= r:
            self._apply(idx, val)
            return
        self._push(idx)
        mid = (nl + nr) // 2
        self._update(l, r, val, idx * 2, nl, mid)
        self._update(l, r, val, idx * 2 + 1, mid + 1, nr)
        self.mx[idx] = max(self.mx[idx * 2], self.mx[idx * 2 + 1])

    def update(self, l: int, r: int, val: int) -> None:
        """
        Interview explanation:
        Helper for the main solution data structure.

        Algorithm:
        - Support the parent algorithm's updates/queries.

        Complexity: Typical fenwick/segtree/DSU bound for this op.
        """
        if self.n == 0 or l > r:
            return
        self._update(l, r, val, 1, 0, self.size - 1)

    def query_max(self) -> int:
        """
        Interview explanation:
        Helper for the main solution data structure.

        Algorithm:
        - Support the parent algorithm's updates/queries.

        Complexity: Typical fenwick/segtree/DSU bound for this op.
        """
        return self.mx[1]


class _IndexSet:
    """Index multiset supporting add/remove and O(log) amortized min/max."""

    def __init__(self) -> None:
        self.alive: set[int] = set()
        self.min_h: list[int] = []
        self.max_h: list[int] = []

    def add(self, x: int) -> None:
        """
        Interview explanation:
        Helper for the main solution data structure.

        Algorithm:
        - Support the parent algorithm's updates/queries.

        Complexity: Typical fenwick/segtree/DSU bound for this op.
        """
        self.alive.add(x)
        heapq.heappush(self.min_h, x)
        heapq.heappush(self.max_h, -x)

    def remove(self, x: int) -> None:
        """
        Interview explanation:
        Helper for the main solution data structure.

        Algorithm:
        - Support the parent algorithm's updates/queries.

        Complexity: Typical fenwick/segtree/DSU bound for this op.
        """
        self.alive.discard(x)

    def __bool__(self) -> bool:
        return bool(self.alive)

    def bounds(self) -> tuple[int, int]:
        """
        Interview explanation:
        Helper for the main solution data structure.

        Algorithm:
        - Support the parent algorithm's updates/queries.

        Complexity: Typical fenwick/segtree/DSU bound for this op.
        """
        while self.min_h and self.min_h[0] not in self.alive:
            heapq.heappop(self.min_h)
        while self.max_h and (-self.max_h[0]) not in self.alive:
            heapq.heappop(self.max_h)
        return self.min_h[0], -self.max_h[0]


class Solution:
    def maximumCount(self, nums: List[int], queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        For split k (prefix ends at k-1), answer = |distinct primes in prefix| +
        |distinct primes in suffix| = |P| + (#primes whose occurrence span
        covers the cut). Maintain each prime's [L,R] and a range-add/max
        segment tree over cut positions.

        Algorithm:
        - Sieve primality to 1e5.
        - For prime with bounds (L,R), add +1 on [L, n-1] and +1 on [0, R-1]
          (SUMFI encoding of single + double coverage).
        - On point update: undo old prime interval, edit index sets, apply new.
        - Answer = tree maximum after each query.

        Complexity: O((n+q) log n) after sieve O(V log log V).
        """
        MAXV = 10**5 + 1
        is_prime = [False, False] + [True] * (MAXV - 2)
        for i in range(2, int(MAXV**0.5) + 1):
            if is_prime[i]:
                for j in range(i * i, MAXV, i):
                    is_prime[j] = False

        n = len(nums)
        seg = _SegTree(n)
        pos: dict[int, _IndexSet] = {}

        def apply_bounds(L: int, R: int, delta: int) -> None:
            if L >= 0:
                seg.update(L, n - 1, delta)
            if R >= 0:
                seg.update(0, R - 1, delta)

        def ask(p: int) -> tuple[int, int]:
            s = pos.get(p)
            if not s:
                return -1, -1
            return s.bounds()

        def add_idx(idx: int) -> None:
            v = nums[idx]
            if not is_prime[v]:
                return
            if v not in pos:
                pos[v] = _IndexSet()
            pos[v].add(idx)

        def rem_idx(idx: int) -> None:
            v = nums[idx]
            if not is_prime[v]:
                return
            pos[v].remove(idx)
            if not pos[v]:
                del pos[v]

        for i in range(n):
            add_idx(i)
        for p, s in pos.items():
            L, R = s.bounds()
            apply_bounds(L, R, 1)

        ans: List[int] = []
        for idx, val in queries:
            if nums[idx] != val:
                old = nums[idx]
                if is_prime[old]:
                    L1, R1 = ask(old)
                    apply_bounds(L1, R1, -1)
                    rem_idx(idx)
                    L2, R2 = ask(old)
                    apply_bounds(L2, R2, 1)
                nums[idx] = val
                if is_prime[val]:
                    L1, R1 = ask(val)
                    apply_bounds(L1, R1, -1)
                    add_idx(idx)
                    L2, R2 = ask(val)
                    apply_bounds(L2, R2, 1)
            ans.append(seg.query_max())
        return ans
# @lc code=end

