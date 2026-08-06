#
# @lc app=leetcode id=1574 lang=python3
#
# [1574] Shortest Subarray to be Removed to Make Array Sorted
#
# https://leetcode.com/problems/shortest-subarray-to-be-removed-to-make-array-sorted/description/
#
# algorithms
# Medium (51.27%)
# Likes:    2492
# Dislikes: 164
# Total Accepted:    131K
# Total Submissions: 256K
# Testcase Example:  "[11,10,18,14,12,11,16,20,13,11]"
#
# Given an integer array arr, remove a subarray (can be empty) from arr such
# that the remaining elements in arr are non-decreasing.
#
# Return the length of the shortest subarray to remove.
#
# A subarray is a contiguous subsequence of the array.
#
# Example 1:
#
# Input: arr = [1,2,3,10,4,2,3,5]
# Output: 3
# Explanation: The shortest subarray we can remove is [10,4,2] of length 3. The
# remaining elements after that will be [1,2,3,3,5] which are sorted.
# Another correct solution is to remove the subarray [3,10,4].
#
# Example 2:
#
# Input: arr = [5,4,3,2,1]
# Output: 4
# Explanation: Since the array is strictly decreasing, we can only keep a
# single element. Therefore we need to remove a subarray of length 4, either
# [5,4,3,2] or [4,3,2,1].
#
# Example 3:
#
# Input: arr = [1,2,3]
# Output: 0
# Explanation: The array is already non-decreasing. We do not need to remove
# any elements.
#
# Constraints:
#
# 1 <= arr.length <= 10^5
#
# 0 <= arr[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def findLengthOfShortestSubarray(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Remove one contiguous subarray to make array nondecreasing. Keep a
        nondecreasing prefix and suffix; minimize removed = n - kept.
        Two pointers: for each prefix end, advance suffix start until
        arr[left]<=arr[right].

        Algorithm:
        - Find start r of longest nondecreasing suffix.
        - ans = r (remove prefix before r).
        - Grow nondecreasing prefix with i; for each i < r advance r while
          arr[i] > arr[r]; ans = min(ans, r-i-1).

        Complexity: O(n) time, O(1) space.
        """
        n = len(arr)
        r = n - 1
        while r > 0 and arr[r - 1] <= arr[r]:
            r -= 1
        ans = r
        i = 0
        while i < r and (i == 0 or arr[i - 1] <= arr[i]):
            while r < n and arr[i] > arr[r]:
                r += 1
            ans = min(ans, r - i - 1)
            i += 1
        return ans
# @lc code=end

