#
# @lc app=leetcode id=1588 lang=python3
#
# [1588] Sum of All Odd Length Subarrays
#
# https://leetcode.com/problems/sum-of-all-odd-length-subarrays/description/
#
# algorithms
# Easy (84.1%)
# Likes:    3934
# Dislikes: 331
# Total Accepted:    266K
# Total Submissions: 317K
# Testcase Example:  "[1,4,2,5,3]"
#
# Given an array of positive integers arr, return the sum of all possible
# odd-length subarrays of arr.
#
# A subarray is a contiguous subsequence of the array.
#
# Example 1:
#
# Input: arr = [1,4,2,5,3]
# Output: 58
# Explanation: The odd-length subarrays of arr and their sums are:
# [1] = 1
# [4] = 4
# [2] = 2
# [5] = 5
# [3] = 3
# [1,4,2] = 7
# [4,2,5] = 11
# [2,5,3] = 10
# [1,4,2,5,3] = 15
# If we add all these together we get 1 + 4 + 2 + 5 + 3 + 7 + 11 + 10 + 15 = 58
#
# Example 2:
#
# Input: arr = [1,2]
# Output: 3
# Explanation: There are only 2 subarrays of odd length, [1] and [2]. Their sum
# is 3.
#
# Example 3:
#
# Input: arr = [10,11,12]
# Output: 66
#
# Constraints:
#
# 1 <= arr.length <= 100
#
# 1 <= arr[i] <= 1000
#
# Follow up:
#
# Could you solve this problem in O(n) time complexity?
#

# @lc code=start
from typing import List


class Solution:
    def sumOddLengthSubarrays(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Contribution: arr[i] appears in ((i+1)* (n-i) + 1) // 2 odd-length
        subarrays (left choices * right choices, take odd lengths).

        Algorithm (contribution):
        - ans = sum(arr[i] * ((i+1)*(n-i)+1)//2 for i)

        Complexity: O(n) time, O(1) space.
        """
        n = len(arr)
        ans = 0
        for i, v in enumerate(arr):
            ans += v * (((i + 1) * (n - i) + 1) // 2)
        return ans

    def sumOddLengthSubarrays_brute(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Alternate: enumerate all odd lengths and subarray sums (prefix optional).

        Algorithm:
        - For length 1,3,5,... sum each window.

        Complexity: O(n^2).
        """
        n = len(arr)
        ans = 0
        for length in range(1, n + 1, 2):
            s = sum(arr[:length])
            ans += s
            for i in range(length, n):
                s += arr[i] - arr[i - length]
                ans += s
        return ans
# @lc code=end

