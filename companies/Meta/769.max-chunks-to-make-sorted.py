#
# @lc app=leetcode id=769 lang=python3
#
# [769] Max Chunks To Make Sorted
#
# https://leetcode.com/problems/max-chunks-to-make-sorted/description/
#
# algorithms
# Medium (64.22%)
# Likes:    3679
# Dislikes: 371
# Total Accepted:    243K
# Total Submissions: 378K
# Testcase Example:  "[4,3,2,1,0]"
#
# You are given an integer array arr of length n that represents a permutation
# of the integers in the range [0, n - 1].
#
# We split arr into some number of chunks (i.e., partitions), and individually
# sort each chunk. After concatenating them, the result should equal the sorted
# array.
#
# Return the largest number of chunks we can make to sort the array.
#
# Example 1:
#
# Input: arr = [4,3,2,1,0]
# Output: 1
# Explanation:
# Splitting into two or more chunks will not return the required result.
# For example, splitting into [4, 3], [2, 1, 0] will result in [3, 4, 0, 1, 2],
# which isn't sorted.
#
# Example 2:
#
# Input: arr = [1,0,2,3,4]
# Output: 4
# Explanation:
# We can split into two chunks, such as [1, 0], [2, 3, 4].
# However, splitting into [1, 0], [2], [3], [4] is the highest number of chunks
# possible.
#
# Constraints:
#
# n == arr.length
#
# 1 <= n <= 10
#
# 0 <= arr[i] < n
#
# All the elements of arr are unique.
#


# @lc code=start
from typing import List


class Solution:
    def maxChunksToSorted(self, arr: List[int]) -> int:
        """
        Interview explanation:
        arr is a permutation of 0..n-1. A chunk ending at i is valid iff the
        max value so far equals i (all values 0..i are in arr[:i+1]).

        Algorithm:
        - mx = chunks = 0; for i,x: mx=max(mx,x); if mx==i: chunks++

        Complexity: O(n) time, O(1) space.
        """
        mx = chunks = 0
        for i, x in enumerate(arr):
            mx = max(mx, x)
            if mx == i:
                chunks += 1
        return chunks
# @lc code=end

