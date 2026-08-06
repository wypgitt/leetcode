#
# @lc app=leetcode id=703 lang=python3
#
# [703] Kth Largest Element in a Stream
#
# https://leetcode.com/problems/kth-largest-element-in-a-stream/description/
#
# algorithms
# Easy (61.42%)
# Likes:    6519
# Dislikes: 4097
# Total Accepted:    1.0M
# Total Submissions: 1.7M
# Testcase Example:  "[\"KthLargest\",\"add\",\"add\",\"add\",\"add\",\"add\"]"
#
# You are part of a university admissions office and need to keep track of the
# kth highest test score from applicants in real-time. This helps to determine
# cut-off marks for interviews and admissions dynamically as new applicants
# submit their scores.
#
# You are tasked to implement a class which, for a given integer k, maintains a
# stream of test scores and continuously returns the kth highest test score
# after a new score has been submitted. More specifically, we are looking for
# the kth highest score in the sorted list of all scores.
#
# Implement the KthLargest class:
#
# KthLargest(int k, int[] nums) Initializes the object with the integer k and
# the stream of test scores nums.
#
# int add(int val) Adds a new test score val to the stream and returns the
# element representing the k^th largest element in the pool of test scores so
# far.
#
# Example 1:
#
# Input:
#
# ["KthLargest", "add", "add", "add", "add", "add"]
#
# [[3, [4, 5, 8, 2]], [3], [5], [10], [9], [4]]
#
# Output: [null, 4, 5, 5, 8, 8]
#
# Explanation:
#
# KthLargest kthLargest = new KthLargest(3, [4, 5, 8, 2]);
#
# kthLargest.add(3); // return 4
#
# kthLargest.add(5); // return 5
#
# kthLargest.add(10); // return 5
#
# kthLargest.add(9); // return 8
#
# kthLargest.add(4); // return 8
#
# Example 2:
#
# Input:
#
# ["KthLargest", "add", "add", "add", "add"]
#
# [[4, [7, 7, 7, 7, 8, 3]], [2], [10], [9], [9]]
#
# Output: [null, 7, 7, 7, 8]
#
# Explanation:
#
# KthLargest kthLargest = new KthLargest(4, [7, 7, 7, 7, 8, 3]);
#
# kthLargest.add(2); // return 7
#
# kthLargest.add(10); // return 7
#
# kthLargest.add(9); // return 7
#
# kthLargest.add(9); // return 8
#
# Constraints:
#
# 0 <= nums.length <= 10^4
#
# 1 <= k <= nums.length + 1
#
# -10^4 <= nums[i] <= 10^4
#
# -10^4 <= val <= 10^4
#
# At most 10^4 calls will be made to add.
#

# @lc code=start
import heapq
from typing import List


class KthLargest:
    def __init__(self, k: int, nums: List[int]):
        """
        Interview explanation:
        Stream k-th largest via a min-heap of size k: heap top is the k-th
        largest among elements seen.

        Algorithm:
        - Keep heap of at most k elements; push all nums then pop while > k.

        Complexity: O(n log k) init, O(k) space.
        """
        self.k = k
        self.heap = list(nums)
        heapq.heapify(self.heap)
        while len(self.heap) > k:
            heapq.heappop(self.heap)

    def add(self, val: int) -> int:
        """
        Interview explanation:
        Insert val into the size-k min-heap; if heap exceeds k, pop smallest.
        Return heap[0] as current k-th largest.

        Algorithm:
        - heappush; if len > k heappop; return heap[0].

        Complexity: O(log k) time, O(1) extra space.
        """
        heapq.heappush(self.heap, val)
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)
        return self.heap[0]


# Your KthLargest object will be instantiated and called as such:
# obj = KthLargest(k, nums)
# param_1 = obj.add(val)
# @lc code=end
