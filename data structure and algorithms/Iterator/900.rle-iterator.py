#
# @lc app=leetcode id=900 lang=python3
#
# [900] RLE Iterator
#
# https://leetcode.com/problems/rle-iterator/description/
#
# algorithms
# Medium (59.49%)
# Likes:    772
# Dislikes: 202
# Total Accepted:    92.2K
# Total Submissions: 155K
# Testcase Example:  "[\"RLEIterator\",\"next\",\"next\",\"next\",\"next\"]"
#
# We can use run-length encoding (i.e., RLE) to encode a sequence of integers.
# In a run-length encoded array of even length encoding (0-indexed), for all
# even i, encoding[i] tells us the number of times that the non-negative
# integer value encoding[i + 1] is repeated in the sequence.
#
# For example, the sequence arr = [8,8,8,5,5] can be encoded to be encoding =
# [3,8,2,5]. encoding = [3,8,0,9,2,5] and encoding = [2,8,1,8,2,5] are also
# valid RLE of arr.
#
# Given a run-length encoded array, design an iterator that iterates through
# it.
#
# Implement the RLEIterator class:
#
# RLEIterator(int[] encoded) Initializes the object with the encoded array
# encoded.
#
# int next(int n) Exhausts the next n elements and returns the last element
# exhausted in this way. If there is no element left to exhaust, return -1
# instead.
#
# Example 1:
#
# Input
# ["RLEIterator", "next", "next", "next", "next"]
# [[[3, 8, 0, 9, 2, 5]], [2], [1], [1], [2]]
# Output
# [null, 8, 8, 5, -1]
#
# Explanation
# RLEIterator rLEIterator = new RLEIterator([3, 8, 0, 9, 2, 5]); // This maps
# to the sequence [8,8,8,5,5].
# rLEIterator.next(2); // exhausts 2 terms of the sequence, returning 8. The
# remaining sequence is now [8, 5, 5].
# rLEIterator.next(1); // exhausts 1 term of the sequence, returning 8. The
# remaining sequence is now [5, 5].
# rLEIterator.next(1); // exhausts 1 term of the sequence, returning 5. The
# remaining sequence is now [5].
# rLEIterator.next(2); // exhausts 2 terms, returning -1. This is because the
# first term exhausted was 5,
# but the second term did not exist. Since the last term exhausted does not
# exist, we return -1.
#
# Constraints:
#
# 2 <= encoding.length <= 1000
#
# encoding.length is even.
#
# 0 <= encoding[i] <= 10^9
#
# 1 <= n <= 10^9
#
# At most 1000 calls will be made to next.
#

# @lc code=start
from typing import List


class RLEIterator:
    def __init__(self, encoding: List[int]):
        """
        Interview explanation:
        Run-length encoding iterator: encoding[2i]=count, encoding[2i+1]=value.
        Exhaust n elements across runs; return last exhausted value or -1.

        Algorithm:
        - Store encoding; index i into current run.

        Complexity: O(1) init (or O(m) copy).
        """
        self.enc = encoding
        self.i = 0

    def next(self, n: int) -> int:
        """
        Interview explanation:
        Consume n from current/future runs; skip empty runs.

        Algorithm:
        - While n and runs remain: if enc[i]>=n: deduct and return val; else
          n-=enc[i], advance i by 2. If exhausted return -1.

        Complexity: O(m) amortized over all next calls (each run skipped once).
        """
        while self.i < len(self.enc):
            if self.enc[self.i] >= n:
                self.enc[self.i] -= n
                return self.enc[self.i + 1]
            n -= self.enc[self.i]
            self.i += 2
        return -1


# Your RLEIterator object will be instantiated and called as such:
# obj = RLEIterator(encoding)
# param_1 = obj.next(n)
# @lc code=end

