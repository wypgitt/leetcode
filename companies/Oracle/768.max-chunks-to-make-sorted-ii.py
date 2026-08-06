#
# @lc app=leetcode id=768 lang=python3
#
# [768] Max Chunks To Make Sorted II
#
# https://leetcode.com/problems/max-chunks-to-make-sorted-ii/description/
#
# algorithms
# Hard (55.02%)
# Likes:    2011
# Dislikes: 63
# Total Accepted:    89.7K
# Total Submissions: 163K
# Testcase Example:  "[5,4,3,2,1]"
#
# You are given an integer array arr.
#
# We split arr into some number of chunks (i.e., partitions), and individually
# sort each chunk. After concatenating them, the result should equal the sorted
# array.
#
# Return the largest number of chunks we can make to sort the array.
#
# Example 1:
#
# Input: arr = [5,4,3,2,1]
# Output: 1
# Explanation:
# Splitting into two or more chunks will not return the required result.
# For example, splitting into [5, 4], [3, 2, 1] will result in [4, 5, 1, 2, 3],
# which isn't sorted.
#
# Example 2:
#
# Input: arr = [2,1,3,4,4]
# Output: 4
# Explanation:
# We can split into two chunks, such as [2, 1], [3, 4, 4].
# However, splitting into [2, 1], [3], [4], [4] is the highest number of chunks
# possible.
#
# Constraints:
#
# 1 <= arr.length <= 2000
#
# 0 <= arr[i] <= 10^8
#


# @lc code=start
from typing import List


class Solution:
    def maxChunksToSorted(self, arr: List[int]) -> int:
        """
        Interview explanation:
        With duplicates allowed, a chunk boundary after i is valid iff
        max(arr[:i+1]) <= min(arr[i+1:]). Precompute right minima; scan left
        maxima and count such boundaries (+1 for the whole array).

        Algorithm:
        - right_min[i] = min(arr[i:]); left_max running
        - chunks = 1; for i in 0..n-2: if left_max <= right_min[i+1]: chunks++

        Complexity: O(n) time, O(n) space.
        """
        n = len(arr)
        if n == 0:
            return 0
        right_min = [0] * n
        right_min[-1] = arr[-1]
        for i in range(n - 2, -1, -1):
            right_min[i] = min(right_min[i + 1], arr[i])
        chunks = 1
        left_max = arr[0]
        for i in range(n - 1):
            left_max = max(left_max, arr[i])
            if left_max <= right_min[i + 1]:
                chunks += 1
        return chunks
# @lc code=end

