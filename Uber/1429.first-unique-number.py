#
# @lc app=leetcode id=1429 lang=python3
#
# [1429] First Unique Number
#
# https://leetcode.com/problems/first-unique-number/description/
#
# algorithms
# Medium (57.84%)
# Likes:    607
# Dislikes: 36
# Total Accepted:    117.4K
# Total Submissions: 203K
# Testcase Example:  "[\"FirstUnique\",\"showFirstUnique\",\"add\",\"showFirstUnique\",\"add\",\"showFirstUnique\",\"add\",\"showFirstUnique\"]\n[[[2,3,5]],[],[5],[],[2],[],[3],[]]"
#
#
# You have a queue of integers, you need to retrieve the first unique
# integer in the queue.
#
# Implement the FirstUnique class:
#
# FirstUnique(int[] nums) Initializes the object with the numbers in the
# queue.
#
# int showFirstUnique() returns the value of the first unique integer of
# the queue, and returns -1 if there is no such integer.
#
# void add(int value) insert value to the queue.
#
# Example 1:
#
# Input:
# ["FirstUnique","showFirstUnique","add","showFirstUnique","add","showFirstUnique","add","showFirstUnique"]
# [[[2,3,5]],[],[5],[],[2],[],[3],[]]
# Output:
# [null,2,null,2,null,3,null,-1]
# Explanation:
# FirstUnique firstUnique = new FirstUnique([2,3,5]);
# firstUnique.showFirstUnique(); // return 2
# firstUnique.add(5);            // the queue is now [2,3,5,5]
# firstUnique.showFirstUnique(); // return 2
# firstUnique.add(2);            // the queue is now [2,3,5,5,2]
# firstUnique.showFirstUnique(); // return 3
# firstUnique.add(3);            // the queue is now [2,3,5,5,2,3]
# firstUnique.showFirstUnique(); // return -1
#
# Example 2:
#
# Input:
# ["FirstUnique","showFirstUnique","add","add","add","add","add","showFirstUnique"]
# [[[7,7,7,7,7,7]],[],[7],[3],[3],[7],[17],[]]
# Output:
# [null,-1,null,null,null,null,null,17]
# Explanation:
# FirstUnique firstUnique = new FirstUnique([7,7,7,7,7,7]);
# firstUnique.showFirstUnique(); // return -1
# firstUnique.add(7);            // the queue is now [7,7,7,7,7,7,7]
# firstUnique.add(3);            // the queue is now [7,7,7,7,7,7,7,3]
# firstUnique.add(3);            // the queue is now [7,7,7,7,7,7,7,3,3]
# firstUnique.add(7);            // the queue is now [7,7,7,7,7,7,7,3,3,7]
# firstUnique.add(17);           // the queue is now
# [7,7,7,7,7,7,7,3,3,7,17]
# firstUnique.showFirstUnique(); // return 17
#
# Example 3:
#
# Input:
# ["FirstUnique","showFirstUnique","add","showFirstUnique"]
# [[[809]],[],[809],[]]
# Output:
# [null,809,null,-1]
# Explanation:
# FirstUnique firstUnique = new FirstUnique([809]);
# firstUnique.showFirstUnique(); // return 809
# firstUnique.add(809);          // the queue is now [809,809]
# firstUnique.showFirstUnique(); // return -1
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^8
#
# 1 <= value <= 10^8
#
# At most 50000 calls will be made to showFirstUnique and add.
#
# @lc code=start
from typing import List
from collections import deque, Counter, OrderedDict


class FirstUnique:
    def __init__(self, nums: List[int]):
        """
        Interview explanation:
        Premium design. Stream of numbers; showFirstUnique returns first unique
        in insertion order (or -1); add inserts. Queue + frequency map: queue
        holds candidates; lazy skip non-unique at front.

        Algorithm:
        - Counter freqs; deque q of values in order; add all nums.

        Complexity: O(n) init.
        """
        self.freq = Counter()
        self.q = deque()
        for x in nums:
            self.add(x)

    def showFirstUnique(self) -> int:
        """
        Interview explanation:
        Pop from left while front's frequency != 1; return front or -1.

        Algorithm:
        - While q and freq[q[0]]!=1: popleft; return q[0] if q else -1.

        Complexity: Amortized O(1).
        """
        while self.q and self.freq[self.q[0]] != 1:
            self.q.popleft()
        return self.q[0] if self.q else -1

    def add(self, value: int) -> None:
        """
        Interview explanation:
        Increment frequency; if first occurrence enqueue as unique candidate.

        Algorithm:
        - freq[value]+=1; if ==1: append to q.

        Complexity: O(1).
        """
        self.freq[value] += 1
        if self.freq[value] == 1:
            self.q.append(value)


class FirstUnique_ordered:
    """Alternate OrderedDict of unique values + set of duplicates."""

    def __init__(self, nums: List[int]):
        """
        Interview explanation:
        Alternate: OrderedDict stores current uniques in order; dup set for seen>1.

        Algorithm:
        - unique OrderedDict; dup set; add each initial num.

        Complexity: O(n) init.
        """
        self.unique = OrderedDict()
        self.dup = set()
        for x in nums:
            self.add(x)

    def showFirstUnique(self) -> int:
        """
        Interview explanation:
        Return first key in OrderedDict or -1.

        Algorithm:
        - next(iter(unique), -1)

        Complexity: O(1).
        """
        return next(iter(self.unique), -1)

    def add(self, value: int) -> None:
        """
        Interview explanation:
        If already dup ignore; if in unique move to dup; else insert unique.

        Algorithm:
        - Branch on membership of dup/unique.

        Complexity: O(1).
        """
        if value in self.dup:
            return
        if value in self.unique:
            del self.unique[value]
            self.dup.add(value)
        else:
            self.unique[value] = None
# @lc code=end
