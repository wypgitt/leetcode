#
# @lc app=leetcode id=845 lang=python3
#
# [845] Longest Mountain in Array
#
# https://leetcode.com/problems/longest-mountain-in-array/description/
#
# algorithms
# Medium (42.39%)
# Likes:    3080
# Dislikes: 94
# Total Accepted:    211K
# Total Submissions: 499K
# Testcase Example:  "[2,1,4,7,3,2,5]"
#
# You may recall that an array arr is a mountain array if and only if:
#
# arr.length >= 3
#
# There exists some index i (0-indexed) with 0 < i < arr.length - 1 such that:
#
# arr[0] < arr[1] < ... < arr[i - 1] < arr[i]
#
# arr[i] > arr[i + 1] > ... > arr[arr.length - 1]
#
# Given an integer array arr, return the length of the longest subarray, which
# is a mountain. Return 0 if there is no mountain subarray.
#
# Example 1:
#
# Input: arr = [2,1,4,7,3,2,5]
# Output: 5
# Explanation: The largest mountain is [1,4,7,3,2] which has length 5.
#
# Example 2:
#
# Input: arr = [2,2,2]
# Output: 0
# Explanation: There is no mountain.
#
# Constraints:
#
# 1 <= arr.length <= 10^4
#
# 0 <= arr[i] <= 10^4
#
# Follow up:
#
# Can you solve it using only one pass?
#
# Can you solve it in O(1) space?
#

# @lc code=start

from typing import List


class Solution:
    def longestMountain(self, arr: List[int]) -> int:
        """
        Interview explanation:
        A mountain is strict increase then strict decrease length ≥ 3. One-pass:
        expand up then down from each potential peak / walk with state.

        Algorithm:
        - For each base i, climb while increasing, then descend while decreasing;
          if both sides nonempty update max length; advance i.

        Complexity: O(n) time, O(1) space.
        """
        n = len(arr)
        ans = 0
        i = 1
        while i < n - 1:
            if arr[i - 1] < arr[i] > arr[i + 1]:
                l = r = i
                while l > 0 and arr[l - 1] < arr[l]:
                    l -= 1
                while r + 1 < n and arr[r] > arr[r + 1]:
                    r += 1
                ans = max(ans, r - l + 1)
                i = r
            else:
                i += 1
        return ans

    def longestMountain_dp(self, arr: List[int]) -> int:
        """
        Interview explanation:
        DP alternate: up[i]=longest increasing ending at i; down[i]=longest
        decreasing starting at i; mountain = up[i]+down[i]-1 when both >1.

        Algorithm:
        - Fill up left→right; down right→left; max over peaks.

        Complexity: O(n) time, O(n) space.
        """
        n = len(arr)
        up = [1] * n
        down = [1] * n
        for i in range(1, n):
            if arr[i] > arr[i - 1]:
                up[i] = up[i - 1] + 1
        for i in range(n - 2, -1, -1):
            if arr[i] > arr[i + 1]:
                down[i] = down[i + 1] + 1
        ans = 0
        for i in range(n):
            if up[i] > 1 and down[i] > 1:
                ans = max(ans, up[i] + down[i] - 1)
        return ans
# @lc code=end
