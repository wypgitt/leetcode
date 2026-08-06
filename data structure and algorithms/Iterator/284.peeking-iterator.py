#
# @lc app=leetcode id=284 lang=python3
#
# [284] Peeking Iterator
#
# https://leetcode.com/problems/peeking-iterator/description/
#
# algorithms
# Medium (61.79%)
# Likes:    1922
# Dislikes: 1053
# Total Accepted:    263K
# Total Submissions: 425K
# Testcase Example:  "[\"PeekingIterator\",\"next\",\"peek\",\"next\",\"next\",\"hasNext\"]"
#
# Design an iterator that supports the peek operation on an existing iterator
# in addition to the hasNext and the next operations.
#
# Implement the PeekingIterator class:
#
# PeekingIterator(Iterator<int> nums) Initializes the object with the given
# integer iterator iterator.
#
# int next() Returns the next element in the array and moves the pointer to the
# next element.
#
# boolean hasNext() Returns true if there are still elements in the array.
#
# int peek() Returns the next element in the array without moving the pointer.
#
# Note: Each language may have a different implementation of the constructor
# and Iterator, but they all support the int next() and boolean hasNext()
# functions.
#
# Example 1:
#
# Input
# ["PeekingIterator", "next", "peek", "next", "next", "hasNext"]
# [[[1, 2, 3]], [], [], [], [], []]
# Output
# [null, 1, 2, 2, 3, false]
#
# Explanation
# PeekingIterator peekingIterator = new PeekingIterator([1, 2, 3]); // [1,2,3]
# peekingIterator.next(); // return 1, the pointer moves to the next element
# [1,2,3].
# peekingIterator.peek(); // return 2, the pointer does not move [1,2,3].
# peekingIterator.next(); // return 2, the pointer moves to the next element
# [1,2,3]
# peekingIterator.next(); // return 3, the pointer moves to the next element
# [1,2,3]
# peekingIterator.hasNext(); // return False
#
# Constraints:
#
# 1 <= nums.length <= 1000
#
# 1 <= nums[i] <= 1000
#
# All the calls to next and peek are valid.
#
# At most 1000 calls will be made to next, hasNext, and peek.
#
# Follow up: How would you extend your design to be generic and work with all
# types, not just integer?
#

# @lc code=start
# Below is the interface for Iterator, which is already defined for you.
#
# class Iterator:
#     def __init__(self, nums):
#         """
#         Initializes an iterator object to the beginning of a list.
#         :type nums: List[int]
#         """
#
#     def hasNext(self):
#         """
#         Returns true if the iteration has more elements.
#         :rtype: bool
#         """
#
#     def next(self):
#         """
#         Returns the next element in the iteration.
#         :rtype: int
#         """


class PeekingIterator:
    def __init__(self, iterator):
        """
        Interview explanation:
        Wrap an Iterator with one-element lookahead so peek() does not advance.

        Algorithm:
        - Cache the next value (and whether it exists) on init / after each next.
        - peek returns cache; next returns cache then refreshes; hasNext checks cache.

        Complexity: O(1) per operation.
        """
        self.it = iterator
        self._has = self.it.hasNext()
        self._next = self.it.next() if self._has else None

    def peek(self):
        """
        Interview explanation:
        Return the cached lookahead value without advancing the underlying
        iterator.

        Algorithm:
        - Return _next.

        Complexity: O(1) time, O(1) space.
        """
        return self._next

    def next(self):
        """
        Interview explanation:
        Emit the cached value, then pull the following element into the cache
        (or clear the cache at end).

        Algorithm:
        - Save _next; refresh _has/_next from the wrapped iterator; return saved.

        Complexity: O(1) time, O(1) space.
        """
        val = self._next
        self._has = self.it.hasNext()
        self._next = self.it.next() if self._has else None
        return val

    def hasNext(self):
        """
        Interview explanation:
        There is a next element iff the lookahead cache is filled.

        Algorithm:
        - Return _has.

        Complexity: O(1) time, O(1) space.
        """
        return self._has


# Your PeekingIterator object will be instantiated and called as such:
# iter = PeekingIterator(Iterator(nums))
# while iter.hasNext():
#     val = iter.peek()   # Get the next element but not advance the iterator.
#     iter.next()         # Should return the same value as [val].
# @lc code=end

