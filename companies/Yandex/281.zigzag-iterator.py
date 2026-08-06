#
# @lc app=leetcode id=281 lang=python3
#
# [281] Zigzag Iterator
#
# https://leetcode.com/problems/zigzag-iterator/description/
#
# algorithms
# Medium (67.12%)
# Likes:    712
# Dislikes: 43
# Total Accepted:    115.5K
# Total Submissions: 172.1K
# Testcase Example:  "[1,2]\n[3,4,5,6]"
#
#
# Given two vectors of integers v1 and v2, implement an iterator to return
# their elements alternately.
#
# Implement the ZigzagIterator class:
#
# ZigzagIterator(List<int> v1, List<int> v2) initializes the object with
# the two vectors v1 and v2.
#
# boolean hasNext() returns true if the iterator still has elements, and
# false otherwise.
#
# int next() returns the current element of the iterator and moves the
# iterator to the next element.
#
# Example 1:
#
# Input: v1 = [1,2], v2 = [3,4,5,6]
# Output: [1,3,2,4,5,6]
# Explanation: By calling next repeatedly until hasNext returns false, the
# order of elements returned by next should be: [1,3,2,4,5,6].
#
# Example 2:
#
# Input: v1 = [1], v2 = []
# Output: [1]
#
# Example 3:
#
# Input: v1 = [], v2 = [1]
# Output: [1]
#
# Constraints:
#
# 0 <= v1.length, v2.length <= 1000
#
# 1 <= v1.length + v2.length <= 2000
#
# -2^31 <= v1[i], v2[i] <= 2^31 - 1
#
# Follow up: What if you are given k vectors? How well can your code be
# extended to such cases?
#
# Clarification for the follow-up question:
#
# The "Zigzag" order is not clearly defined and is ambiguous for k > 2
# cases. If "Zigzag" does not look right to you, replace "Zigzag" with
# "Cyclic".
#
# Follow-up Example:
#
# Input: v1 = [1,2,3], v2 = [4,5,6,7], v3 = [8,9]
# Output: [1,4,8,2,5,9,3,6,7]
#
# @lc code=start
from collections import deque
from typing import List


class ZigzagIterator:
    def __init__(self, v1: List[int], v2: List[int]):
        """
        Interview explanation:
        Interleave two (or k) vectors. Keep a queue of (index, vector) pairs for
        non-empty sources; pop front, yield value, re-append if more remain.

        Algorithm:
        - For each non-empty input vector, enqueue (0, vector).

        Complexity: O(k) init for k vectors; O(k) space.
        """
        self.q = deque()
        if v1:
            self.q.append((0, v1))
        if v2:
            self.q.append((0, v2))

    def next(self) -> int:
        """
        Interview explanation:
        Round-robin: take the front source, emit its current element, and
        requeue that source if it still has remaining elements.

        Algorithm:
        - Pop (i, vec); val = vec[i]; if i+1 < len(vec), append (i+1, vec).

        Complexity: O(1) time, O(1) space.
        """
        i, vec = self.q.popleft()
        val = vec[i]
        if i + 1 < len(vec):
            self.q.append((i + 1, vec))
        return val

    def hasNext(self) -> bool:
        """
        Interview explanation:
        Any queued (index, vector) pair means more values remain.

        Algorithm:
        - Return bool(q).

        Complexity: O(1) time, O(1) space.
        """
        return bool(self.q)


# Your ZigzagIterator object will be instantiated and called as such:
# i, v = ZigzagIterator(v1, v2), []
# while i.hasNext(): v.append(i.next())
# @lc code=end

