#
# @lc app=leetcode id=1394 lang=python3
#
# [1394] Find Lucky Integer in an Array
#
# https://leetcode.com/problems/find-lucky-integer-in-an-array/description/
#
# algorithms
# Easy (75.6%)
# Likes:    1651
# Dislikes: 46
# Total Accepted:    354K
# Total Submissions: 468K
# Testcase Example:  "[2,2,3,4]"
#
# Given an array of integers arr, a lucky integer is an integer that has a
# frequency in the array equal to its value.
#
# Return the largest lucky integer in the array. If there is no lucky integer
# return -1.
#
# Example 1:
#
# Input: arr = [2,2,3,4]
# Output: 2
# Explanation: The only lucky number in the array is 2 because frequency[2] ==
# 2.
#
# Example 2:
#
# Input: arr = [1,2,2,3,3,3]
# Output: 3
# Explanation: 1, 2 and 3 are all lucky numbers, return the largest of them.
#
# Example 3:
#
# Input: arr = [2,2,2,3,3]
# Output: -1
# Explanation: There are no lucky numbers in the array.
#
# Constraints:
#
# 1 <= arr.length <= 500
#
# 1 <= arr[i] <= 500
#

# @lc code=start

from typing import List
from collections import Counter


class Solution:
    def findLucky(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Lucky integer appears exactly as many times as its value. Return the
        largest lucky integer, or -1.

        Algorithm:
        - Counter; max of x where cnt[x]==x, else -1

        Complexity: O(n) time, O(U) space.
        """
        cnt = Counter(arr)
        ans = -1
        for x, c in cnt.items():
            if x == c:
                ans = max(ans, x)
        return ans
# @lc code=end
