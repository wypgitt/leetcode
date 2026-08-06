#
# @lc app=leetcode id=1825 lang=python3
#
# [1825] Finding MK Average
#
# https://leetcode.com/problems/finding-mk-average/description/
#
# algorithms
# Hard (38.88%)
# Likes:    530
# Dislikes: 142
# Total Accepted:    29.7K
# Total Submissions: 76.5K
# Testcase Example:  "[\"MKAverage\",\"addElement\",\"addElement\",\"calculateMKAverage\",\"addElement\",\"calculateMKAverage\",\"addElement\",\"addElement\",\"addElement\",\"calculateMKAverage\"]"
#
# You are given two integers, m and k, and a stream of integers. You are tasked
# to implement a data structure that calculates the MKAverage for the stream.
#
# The MKAverage can be calculated using these steps:
#
# If the number of the elements in the stream is less than m you should
# consider the MKAverage to be -1. Otherwise, copy the last m elements of the
# stream to a separate container.
#
# Remove the smallest k elements and the largest k elements from the container.
#
# Calculate the average value for the rest of the elements rounded down to the
# nearest integer.
#
# Implement the MKAverage class:
#
# MKAverage(int m, int k) Initializes the MKAverage object with an empty stream
# and the two integers m and k.
#
# void addElement(int num) Inserts a new element num into the stream.
#
# int calculateMKAverage() Calculates and returns the MKAverage for the current
# stream rounded down to the nearest integer.
#
# Example 1:
#
# Input
# ["MKAverage", "addElement", "addElement", "calculateMKAverage", "addElement",
# "calculateMKAverage", "addElement", "addElement", "addElement",
# "calculateMKAverage"]
# [[3, 1], [3], [1], [], [10], [], [5], [5], [5], []]
# Output
# [null, null, null, -1, null, 3, null, null, null, 5]
#
# Explanation
# MKAverage obj = new MKAverage(3, 1);
# obj.addElement(3); // current elements are [3]
# obj.addElement(1); // current elements are [3,1]
# obj.calculateMKAverage(); // return -1, because m = 3 and only 2 elements
# exist.
# obj.addElement(10); // current elements are [3,1,10]
# obj.calculateMKAverage(); // The last 3 elements are [3,1,10].
# // After removing smallest and largest 1 element the container will be [3].
# // The average of [3] equals 3/1 = 3, return 3
# obj.addElement(5); // current elements are [3,1,10,5]
# obj.addElement(5); // current elements are [3,1,10,5,5]
# obj.addElement(5); // current elements are [3,1,10,5,5,5]
# obj.calculateMKAverage(); // The last 3 elements are [5,5,5].
# // After removing smallest and largest 1 element the container will be [5].
# // The average of [5] equals 5/1 = 5, return 5
#
# Constraints:
#
# 3 <= m <= 10^5
#
# 1 < k*2 < m
#
# 1 <= num <= 10^5
#
# At most 10^5 calls will be made to addElement and calculateMKAverage.
#

# @lc code=start
from collections import deque


class _BIT:
    def __init__(self, n: int):
        """
        Interview explanation:
        Fenwick tree (Binary Indexed Tree) for prefix sums over [1..n].

        Algorithm:
        - Allocate 1-indexed tree array of size n+1.

        Complexity: O(n) space.
        """
        self.n = n
        self.c = [0] * (n + 1)

    def add(self, i: int, v: int) -> None:
        """
        Interview explanation:
        Point update: add v at index i and propagate to responsible ranges.

        Algorithm:
        - While i <= n: c[i] += v; i += i & -i (jump to next covering node).

        Complexity: O(log n).
        """
        while i <= self.n:
            self.c[i] += v
            i += i & -i

    def sum(self, i: int) -> int:
        """
        Interview explanation:
        Prefix sum query for range [1..i].

        Algorithm:
        - Accumulate c[i] while i > 0; i -= i & -i (jump to parent).

        Complexity: O(log n).
        """
        s = 0
        while i > 0:
            s += self.c[i]
            i -= i & -i
        return s


class MKAverage:
    def __init__(self, m: int, k: int):
        """
        Interview explanation:
        Keep last m stream values; MKAverage = floor(sum of values after removing
        k smallest and k largest / (m-2k)). Values in [1,1e5] → Fenwick (BIT)
        on frequencies and value-sums for order-statistic prefix sums.

        Algorithm (queue + Fenwick):
        - BIT freq and BIT sum_val indexed by number.
        - add/remove update both BITs; query sum of middle band via k-th order stats.

        Complexity: O(1) init storing m,k; BITs size 1e5.
        """
        self.m = m
        self.k = k
        self.q = deque()
        self.MAX = 10**5
        self.freq = _BIT(self.MAX)
        self.total = _BIT(self.MAX)

    def _sum_first(self, count: int) -> int:
        """Sum of the smallest `count` elements currently stored."""
        if count <= 0:
            return 0
        # find largest value v such that freq.sum(v) < count, then partial
        lo, hi = 1, self.MAX
        need = count
        ans = 0
        # walk bits from high
        idx = 0
        bit = 1 << 16
        while bit:
            nxt = idx + bit
            if nxt <= self.MAX and self.freq.c[nxt] < need:
                need -= self.freq.c[nxt]
                ans += self.total.c[nxt]
                idx = nxt
            bit >>= 1
        # remaining `need` copies of value idx+1
        return ans + need * (idx + 1)

    def addElement(self, num: int) -> None:
        """
        Interview explanation:
        Append num; if window exceeds m, drop oldest. Update Fenwick counts/sums.

        Algorithm:
        - q.append; freq/total add; if len>m remove left.

        Complexity: O(log V) per call, V=1e5.
        """
        self.q.append(num)
        self.freq.add(num, 1)
        self.total.add(num, num)
        if len(self.q) > self.m:
            old = self.q.popleft()
            self.freq.add(old, -1)
            self.total.add(old, -old)

    def calculateMKAverage(self) -> int:
        """
        Interview explanation:
        Need >= m elements; sum_all - sum(k smallest) - sum(k largest), floor div.

        Algorithm:
        - s_all = total.sum(MAX); s_lo = sum first k; s_hi = s_all - sum first (m-k);
          return (s_all - s_lo - s_hi) // (m-2k).

        Complexity: O(log V).
        """
        if len(self.q) < self.m:
            return -1
        s_all = self.total.sum(self.MAX)
        s_lo = self._sum_first(self.k)
        s_first_m_k = self._sum_first(self.m - self.k)
        s_hi = s_all - s_first_m_k
        return (s_all - s_lo - s_hi) // (self.m - 2 * self.k)
# @lc code=end
