#
# @lc app=leetcode id=1460 lang=python3
#
# [1460] Make Two Arrays Equal by Reversing Subarrays
#
# https://leetcode.com/problems/make-two-arrays-equal-by-reversing-subarrays/description/
#
# algorithms
# Easy (75.82%)
# Likes:    1532
# Dislikes: 164
# Total Accepted:    339K
# Total Submissions: 446K
# Testcase Example:  "[1,2,3,4]"
#
# You are given two integer arrays of equal length target and arr. In one step,
# you can select any non-empty subarray of arr and reverse it. You are allowed
# to make any number of steps.
#
# Return true if you can make arr equal to target or false otherwise.
#
# Example 1:
#
# Input: target = [1,2,3,4], arr = [2,4,1,3]
# Output: true
# Explanation: You can follow the next steps to convert arr to target:
# 1- Reverse subarray [2,4,1], arr becomes [1,4,2,3]
# 2- Reverse subarray [4,2], arr becomes [1,2,4,3]
# 3- Reverse subarray [4,3], arr becomes [1,2,3,4]
# There are multiple ways to convert arr to target, this is not the only way to
# do so.
#
# Example 2:
#
# Input: target = [7], arr = [7]
# Output: true
# Explanation: arr is equal to target without any reverses.
#
# Example 3:
#
# Input: target = [3,7,9], arr = [3,7,11]
# Output: false
# Explanation: arr does not have value 9 and it can never be converted to
# target.
#
# Constraints:
#
# target.length == arr.length
#
# 1 <= target.length <= 1000
#
# 1 <= target[i] <= 1000
#
# 1 <= arr[i] <= 1000
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def canBeEqual(self, target: List[int], arr: List[int]) -> bool:
        """
        Interview explanation:
        Any permutation is reachable by subarray reverses (like pancake/bubble
        sort). Arrays equal iff same multiset.

        Algorithm:
        - Counter(target) == Counter(arr).

        Complexity: O(n) time, O(n) space.
        """
        return Counter(target) == Counter(arr)

    def canBeEqual_sort(self, target: List[int], arr: List[int]) -> bool:
        """
        Interview explanation:
        Alternate: sort both and compare.

        Algorithm:
        - sorted(target) == sorted(arr).

        Complexity: O(n log n) time, O(n) space.
        """
        return sorted(target) == sorted(arr)
# @lc code=end
