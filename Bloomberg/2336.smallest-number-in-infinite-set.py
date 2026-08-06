#
# @lc app=leetcode id=2336 lang=python3
#
# [2336] Smallest Number in Infinite Set
#
# https://leetcode.com/problems/smallest-number-in-infinite-set/description/
#
# algorithms
# Medium (70.66%)
# Likes:    1867
# Dislikes: 234
# Total Accepted:    242K
# Total Submissions: 342.6K
# Testcase Example:  "[\"SmallestInfiniteSet\",\"addBack\",\"popSmallest\",\"popSmallest\",\"popSmallest\",\"addBack\",\"popSmallest\",\"popSmallest\",\"popSmallest\"]\n[[],[2],[],[],[],[1],[],[],[]]"
#
# You have a set which contains all positive integers [1, 2, 3, 4, 5, ...].
#
# Implement the SmallestInfiniteSet class:
#
#
# SmallestInfiniteSet() Initializes the SmallestInfiniteSet object to contain
# all positive integers.
#
#
# int popSmallest() Removes and returns the smallest integer contained in the
# infinite set.
#
#
# void addBack(int num) Adds a positive integer num back into the infinite set,
# if it is not already in the infinite set.
#
#
#
# Example 1:
#
# Input
# ["SmallestInfiniteSet", "addBack", "popSmallest", "popSmallest",
# "popSmallest", "addBack", "popSmallest", "popSmallest", "popSmallest"]
# [[], [2], [], [], [], [1], [], [], []]
# Output
# [null, null, 1, 2, 3, null, 1, 4, 5]
#
# Explanation
# SmallestInfiniteSet smallestInfiniteSet = new SmallestInfiniteSet();
# smallestInfiniteSet.addBack(2);    // 2 is already in the set, so no change is
# made.
# smallestInfiniteSet.popSmallest(); // return 1, since 1 is the smallest
# number, and remove it from the set.
# smallestInfiniteSet.popSmallest(); // return 2, and remove it from the set.
# smallestInfiniteSet.popSmallest(); // return 3, and remove it from the set.
# smallestInfiniteSet.addBack(1);    // 1 is added back to the set.
# smallestInfiniteSet.popSmallest(); // return 1, since 1 was added back to the
# set and
#                                    // is the smallest number, and remove it
# from the set.
# smallestInfiniteSet.popSmallest(); // return 4, and remove it from the set.
# smallestInfiniteSet.popSmallest(); // return 5, and remove it from the set.
#
#
#
# Constraints:
#
#
# 1 <= num <= 1000
#
#
# At most 1000 calls will be made in total to popSmallest and addBack.
#

# @lc code=start
import heapq


class SmallestInfiniteSet:

    def __init__(self):
        """
        Interview explanation:
        Multiset of all positive integers; support pop smallest and add back.

        Algorithm:
        - Track next contiguous integer `cur` from 1; a min-heap + set of
          added-back numbers smaller than cur.

        Complexity: O(1) init space grows with addBacks.
        """
        self.cur = 1
        self.heap = []
        self.in_heap = set()

    def popSmallest(self) -> int:
        """
        Interview explanation:
        Remove and return the smallest positive integer currently in the set.

        Algorithm:
        - If heap nonempty, pop heap min; else take cur and increment.

        Complexity: O(log n) time.
        """
        if self.heap:
            x = heapq.heappop(self.heap)
            self.in_heap.remove(x)
            return x
        x = self.cur
        self.cur += 1
        return x

    def addBack(self, num: int) -> None:
        """
        Interview explanation:
        Add num back if it was previously popped (not currently present).

        Algorithm:
        - If num < cur and not already in heap, push it.

        Complexity: O(log n) time.
        """
        if num < self.cur and num not in self.in_heap:
            heapq.heappush(self.heap, num)
            self.in_heap.add(num)


# Your SmallestInfiniteSet object will be instantiated and called as such:
# obj = SmallestInfiniteSet()
# param_1 = obj.popSmallest()
# obj.addBack(num)
# @lc code=end
