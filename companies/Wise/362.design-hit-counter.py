#
# @lc app=leetcode id=362 lang=python3
#
# [362] Design Hit Counter
#
# https://leetcode.com/problems/design-hit-counter/description/
#
# algorithms
# Medium (69.74%)
# Likes:    2153
# Dislikes: 257
# Total Accepted:    347.2K
# Total Submissions: 497.9K
# Testcase Example:  "[\"HitCounter\",\"hit\",\"hit\",\"hit\",\"getHits\",\"hit\",\"getHits\",\"getHits\"]\n[[],[1],[2],[3],[4],[300],[300],[301]]"
#
#
# Design a hit counter which counts the number of hits received in the
# past 5 minutes (i.e., the past 300 seconds).
#
# Your system should accept a timestamp parameter (in seconds
# granularity), and you may assume that calls are being made to the system
# in chronological order (i.e., timestamp is monotonically increasing).
# Several hits may arrive roughly at the same time.
#
# Implement the HitCounter class:
#
# HitCounter() Initializes the object of the hit counter system.
#
# void hit(int timestamp) Records a hit that happened at timestamp (in
# seconds). Several hits may happen at the same timestamp.
#
# int getHits(int timestamp) Returns the number of hits in the past 5
# minutes from timestamp (i.e., the past 300 seconds).
#
# Example 1:
#
# Input
# ["HitCounter", "hit", "hit", "hit", "getHits", "hit", "getHits",
# "getHits"]
# [[], [1], [2], [3], [4], [300], [300], [301]]
# Output
# [null, null, null, null, 3, null, 4, 3]
#
# Explanation
# HitCounter hitCounter = new HitCounter();
# hitCounter.hit(1);       // hit at timestamp 1.
# hitCounter.hit(2);       // hit at timestamp 2.
# hitCounter.hit(3);       // hit at timestamp 3.
# hitCounter.getHits(4);   // get hits at timestamp 4, return 3.
# hitCounter.hit(300);     // hit at timestamp 300.
# hitCounter.getHits(300); // get hits at timestamp 300, return 4.
# hitCounter.getHits(301); // get hits at timestamp 301, return 3.
#
# Constraints:
#
# 1 <= timestamp <= 2 * 10^9
#
# All the calls are being made to the system in chronological order (i.e.,
# timestamp is monotonically increasing).
#
# At most 300 calls will be made to hit and getHits.
#
# Follow up: What if the number of hits per second could be huge? Does
# your design scale?
#
# @lc code=start
from collections import deque


class HitCounter:
    """
    Interview explanation:
    Queue of hit timestamps in the last 300 seconds. hit appends; getHits
    pops timestamps <= timestamp - 300, then returns queue length.

    Algorithm:
    - deque of times.
    - hit(t): append t.
    - getHits(t): while front <= t-300 popleft; return len.

    Complexity: amortized O(1) per op, O(hits in window) space.
    """

    def __init__(self):
        """
        Interview explanation:
        Deque of hit timestamps within the rolling 300-second window.

        Algorithm:
        - q = empty deque.

        Complexity: O(1) init, O(hits in window) space.
        """
        self.q = deque()

    def hit(self, timestamp: int) -> None:
        """
        Interview explanation:
        Record a hit at timestamp; eviction happens lazily in getHits.

        Algorithm:
        - Append timestamp to the deque.

        Complexity: O(1) time, O(1) amortized space.
        """
        self.q.append(timestamp)

    def getHits(self, timestamp: int) -> int:
        """
        Interview explanation:
        Drop hits older than 300 seconds, then return how many remain.

        Algorithm:
        - While front <= timestamp - 300: popleft; return len(q).

        Complexity: Amortized O(1) time, O(1) space.
        """
        while self.q and self.q[0] <= timestamp - 300:
            self.q.popleft()
        return len(self.q)


class HitCounterBuckets:
    """
    Interview explanation:
    Alternate: circular buckets of size 300 storing (time, count) for high-
    frequency hit() coalescing when many hits share a second.

    Algorithm:
    - times[300], hits[300].
    - hit: idx = t % 300; if times[idx]==t accumulate else reset.
    - getHits: sum hits where times[i] > t-300.

    Complexity: O(1) hit, O(300) getHits, O(1) space.
    """

    def __init__(self):
        """
        Interview explanation:
        Fixed 300 buckets: each slot holds the timestamp and hit count for
        that second modulo 300.

        Algorithm:
        - times = [0]*300; hits = [0]*300.

        Complexity: O(1) time and space.
        """
        self.times = [0] * 300
        self.hits = [0] * 300

    def hit(self, timestamp: int) -> None:
        """
        Interview explanation:
        Map timestamp into a circular bucket; reset if the slot holds an older
        second, otherwise accumulate.

        Algorithm:
        - idx = t % 300; if times[idx] != t: reset to 1 else hits[idx] += 1.

        Complexity: O(1) time, O(1) space.
        """
        idx = timestamp % 300
        if self.times[idx] != timestamp:
            self.times[idx] = timestamp
            self.hits[idx] = 1
        else:
            self.hits[idx] += 1

    def getHits(self, timestamp: int) -> int:
        """
        Interview explanation:
        Sum bucket counts whose stored time is still inside the 300s window.

        Algorithm:
        - For each i: if timestamp - times[i] < 300, add hits[i].

        Complexity: O(300) time, O(1) space.
        """
        total = 0
        for i in range(300):
            if timestamp - self.times[i] < 300:
                total += self.hits[i]
        return total


# Your HitCounter object will be instantiated and called as such:
# obj = HitCounter()
# obj.hit(timestamp)
# param_2 = obj.getHits(timestamp)
# @lc code=end
