#
# @lc app=leetcode id=2349 lang=python3
#
# [2349] Design a Number Container System
#
# https://leetcode.com/problems/design-a-number-container-system/description/
#
# algorithms
# Medium (57.05%)
# Likes:    969
# Dislikes: 74
# Total Accepted:    150.5K
# Total Submissions: 263.7K
# Testcase Example:  "[\"NumberContainers\",\"find\",\"change\",\"change\",\"change\",\"change\",\"find\",\"change\",\"find\"]\n[[],[10],[2,10],[1,10],[3,10],[5,10],[10],[1,20],[10]]"
#
# Design a number container system that can do the following:
#
#
# Insert or Replace a number at the given index in the system.
#
#
# Return the smallest index for the given number in the system.
#
# Implement the NumberContainers class:
#
#
# NumberContainers() Initializes the number container system.
#
#
# void change(int index, int number) Fills the container at index with the
# number. If there is already a number at that index, replace it.
#
#
# int find(int number) Returns the smallest index for the given number, or -1 if
# there is no index that is filled by number in the system.
#
#
#
# Example 1:
#
# Input
# ["NumberContainers", "find", "change", "change", "change", "change", "find",
# "change", "find"]
# [[], [10], [2, 10], [1, 10], [3, 10], [5, 10], [10], [1, 20], [10]]
# Output
# [null, -1, null, null, null, null, 1, null, 2]
#
# Explanation
# NumberContainers nc = new NumberContainers();
# nc.find(10); // There is no index that is filled with number 10. Therefore, we
# return -1.
# nc.change(2, 10); // Your container at index 2 will be filled with number 10.
# nc.change(1, 10); // Your container at index 1 will be filled with number 10.
# nc.change(3, 10); // Your container at index 3 will be filled with number 10.
# nc.change(5, 10); // Your container at index 5 will be filled with number 10.
# nc.find(10); // Number 10 is at the indices 1, 2, 3, and 5. Since the smallest
# index that is filled with 10 is 1, we return 1.
# nc.change(1, 20); // Your container at index 1 will be filled with number 20.
# Note that index 1 was filled with 10 and then replaced with 20.
# nc.find(10); // Number 10 is at the indices 2, 3, and 5. The smallest index
# that is filled with 10 is 2. Therefore, we return 2.
#
#
#
# Constraints:
#
#
# 1 <= index, number <= 10^9
#
#
# At most 10^5 calls will be made in total to change and find.
#

# @lc code=start
from collections import defaultdict
import heapq


class NumberContainers:

    def __init__(self):
        """
        Interview explanation:
        Map indices to numbers; support change(index,number) and find(number)=
        smallest index holding that number (-1 if none).

        Algorithm:
        - index->number dict; number->min-heap of indices. Lazy deletion on find
          when heap top no longer maps to that number.

        Complexity: O(1) init.
        """
        self.idx = {}
        self.heaps = defaultdict(list)

    def change(self, index: int, number: int) -> None:
        """
        Interview explanation:
        Set/replace the number at index.

        Algorithm:
        - Update idx[index]=number; push index onto that number's heap.

        Complexity: O(log n) time.
        """
        self.idx[index] = number
        heapq.heappush(self.heaps[number], index)

    def find(self, number: int) -> int:
        """
        Interview explanation:
        Smallest index currently containing `number`, else -1.

        Algorithm:
        - Pop stale heap entries until top is valid; return top or -1.

        Complexity: Amortized O(log n) time.
        """
        h = self.heaps[number]
        while h and self.idx.get(h[0]) != number:
            heapq.heappop(h)
        return h[0] if h else -1


# Your NumberContainers object will be instantiated and called as such:
# obj = NumberContainers()
# obj.change(index,number)
# param_2 = obj.find(number)
# @lc code=end
