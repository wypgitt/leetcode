#
# @lc app=leetcode id=1756 lang=python3
#
# [1756] Design Most Recently Used Queue
#
# https://leetcode.com/problems/design-most-recently-used-queue/description/
#
# algorithms
# Medium (78.31%)
# Likes:    338
# Dislikes: 28
# Total Accepted:    27.9K
# Total Submissions: 35.6K
# Testcase Example:  "[\"MRUQueue\",\"fetch\",\"fetch\",\"fetch\",\"fetch\"]\n[[8],[3],[5],[2],[8]]"
#
#
# Design a queue-like data structure that moves the most recently used
# element to the end of the queue.
#
# Implement the MRUQueue class:
#
# MRUQueue(int n) constructs the MRUQueue with n elements: [1,2,3,...,n].
#
# int fetch(int k) moves the k^th element (1-indexed) to the end of the
# queue and returns it.
#
# Example 1:
#
# Input:
# ["MRUQueue", "fetch", "fetch", "fetch", "fetch"]
# [[8], [3], [5], [2], [8]]
# Output:
# [null, 3, 6, 2, 2]
#
# Explanation:
# MRUQueue mRUQueue = new MRUQueue(8); // Initializes the queue to
# [1,2,3,4,5,6,7,8].
# mRUQueue.fetch(3); // Moves the 3^rd element (3) to the end of the queue
# to become [1,2,4,5,6,7,8,3] and returns it.
# mRUQueue.fetch(5); // Moves the 5^th element (6) to the end of the queue
# to become [1,2,4,5,7,8,3,6] and returns it.
# mRUQueue.fetch(2); // Moves the 2^nd element (2) to the end of the queue
# to become [1,4,5,7,8,3,6,2] and returns it.
# mRUQueue.fetch(8); // The 8^th element (2) is already at the end of the
# queue so just return it.
#
# Constraints:
#
# 1 <= n <= 2000
#
# 1 <= k <= n
#
# At most 2000 calls will be made to fetch.
#
# Follow up: Finding an O(n) algorithm per fetch is a bit easy. Can you
# find an algorithm with a better complexity for each fetch call?
#
# @lc code=start
class MRUQueue:
    def __init__(self, n: int):
        """
        Interview explanation:
        Premium design: queue holding 1..n. fetch(k) returns the k-th element
        (1-indexed) and moves it to the end (most recently used).

        Algorithm (list simulation):
        - self.q = list(range(1, n+1))

        Complexity: O(n) init.
        """
        self.q = list(range(1, n + 1))

    def fetch(self, k: int) -> int:
        """
        Interview explanation:
        Remove the 1-indexed k-th element and append it to the end; return it.

        Algorithm:
        - x = q.pop(k-1); q.append(x); return x

        Complexity: O(n) per fetch.
        """
        x = self.q.pop(k - 1)
        self.q.append(x)
        return x


class MRUQueueFenwick:
    """Alternate optimal Fenwick/BIT for O(log n) fetch (move-to-end)."""

    def __init__(self, n: int):
        """
        Interview explanation:
        Map values onto dynamic positions; BIT stores occupancy. fetch(k)
        finds the k-th occupied index, removes it, and reinserts at a new
        rightmost free slot.

        Algorithm:
        - val_at[i]=i for i=1..n; BIT ones; nxt = n+1 for new end slots.

        Complexity: O(n log N) init; N = n + #fetches.
        """
        self.N = n + 2005
        self.bit = [0] * (self.N + 1)
        self.val_at = [0] * (self.N + 1)
        for i in range(1, n + 1):
            self.val_at[i] = i
            self._add(i, 1)
        self.nxt = n + 1

    def _add(self, i: int, v: int) -> None:
        while i <= self.N:
            self.bit[i] += v
            i += i & -i

    def _kth(self, k: int) -> int:
        idx = 0
        bit = 1 << self.N.bit_length()
        while bit:
            nxt = idx + bit
            if nxt <= self.N and self.bit[nxt] < k:
                idx = nxt
                k -= self.bit[nxt]
            bit >>= 1
        return idx + 1

    def fetch(self, k: int) -> int:
        """
        Interview explanation:
        BIT-select the k-th live position; move that value to a fresh end slot.

        Algorithm:
        - p=_kth(k); x=val_at[p]; clear p; place x at nxt; nxt+=1.

        Complexity: O(log N) per fetch.
        """
        p = self._kth(k)
        x = self.val_at[p]
        self._add(p, -1)
        self.val_at[p] = 0
        self.val_at[self.nxt] = x
        self._add(self.nxt, 1)
        self.nxt += 1
        return x


# Your MRUQueue object will be instantiated and called as such:
# obj = MRUQueue(n)
# param_1 = obj.fetch(k)
# @lc code=end
