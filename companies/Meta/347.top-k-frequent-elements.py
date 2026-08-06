#
# @lc app=leetcode id=347 lang=python3
#
# [347] Top K Frequent Elements
#
# https://leetcode.com/problems/top-k-frequent-elements/description/
#
# algorithms
# Medium (67.05%)
# Likes:    19772
# Dislikes: 857
# Total Accepted:    3.8M
# Total Submissions: 5.7M
# Testcase Example:  "[1,1,1,2,2,3]"
#
# Given an integer array nums and an integer k, return the k most frequent
# elements. You may return the answer in any order.
#
# Example 1:
#
# Input: nums = [1,1,1,2,2,3], k = 2
#
# Output: [1,2]
#
# Example 2:
#
# Input: nums = [1], k = 1
#
# Output: [1]
#
# Example 3:
#
# Input: nums = [1,2,1,2,1,2,3,1,3,2], k = 2
#
# Output: [1,2]
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^4 <= nums[i] <= 10^4
#
# k is in the range [1, the number of unique elements in the array].
#
# It is guaranteed that the answer is unique.
#
# Follow up: Your algorithm's time complexity must be better than O(n log n),
# where n is the array's size.
#

# @lc code=start
import heapq
from collections import Counter
from typing import List


class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        Bucket sort by frequency: count with Counter, put numbers into buckets
        indexed by frequency, then collect from highest frequency down until k.

        Algorithm:
        - freq map; buckets[0..n] lists.
        - Scan buckets from n..1, append until k elements.

        Complexity: O(n) time and space — classic linear best.
        """
        count = Counter(nums)
        buckets: List[List[int]] = [[] for _ in range(len(nums) + 1)]
        for num, freq in count.items():
            buckets[freq].append(num)
        res: List[int] = []
        for freq in range(len(buckets) - 1, 0, -1):
            for num in buckets[freq]:
                res.append(num)
                if len(res) == k:
                    return res
        return res

    def topKFrequent_heap(self, nums: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        Alternate classic best: min-heap of size k on (frequency, value), or
        nlargest on Counter items — O(n log k).

        Algorithm:
        - Counter; heapq.nlargest(k, items, key=freq) or maintain size-k heap.

        Complexity: O(n log k) time, O(n) space.
        """
        count = Counter(nums)
        return [num for num, _ in heapq.nlargest(k, count.items(), key=lambda x: x[1])]
# @lc code=end
