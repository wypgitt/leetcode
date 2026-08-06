#
# @lc app=leetcode id=1426 lang=python3
#
# [1426] Counting Elements
#
# https://leetcode.com/problems/counting-elements/description/
#
# algorithms
# Easy (60.81%)
# Likes:    171
# Dislikes: 66
# Total Accepted:    171.2K
# Total Submissions: 281.5K
# Testcase Example:  "[1,2,3]"
#
#
# Given an integer array arr, count how many elements x there are, such
# that x + 1 is also in arr. If there are duplicates in arr, count them
# separately.
#
# Example 1:
#
# Input: arr = [1,2,3]
# Output: 2
# Explanation: 1 and 2 are counted cause 2 and 3 are in arr.
#
# Example 2:
#
# Input: arr = [1,1,3,3,5,5,7,7]
# Output: 0
# Explanation: No numbers are counted, cause there is no 2, 4, 6, or 8 in
# arr.
#
# Constraints:
#
# 1 <= arr.length <= 1000
#
# 0 <= arr[i] <= 1000
#
# @lc code=start
from typing import List


class Solution:
    def countElements(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Premium. Count elements x in arr such that x+1 also appears in arr.

        Algorithm:
        (hash set)
        - S=set(arr); sum(1 for x in arr if x+1 in S)

        Complexity: O(n) time, O(n) space.
        """
        s = set(arr)
        return sum(1 for x in arr if x + 1 in s)

    def countElements_sort(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Alternate: sort unique check via two pointers / binary search presence
        of x+1 on sorted unique, then count frequencies of valid x.

        Algorithm:
        - Counter; for each x with freq, if x+1 in counter add freq.

        Complexity: O(n) time with counter, O(n) space.
        """
        from collections import Counter
        cnt = Counter(arr)
        return sum(freq for x, freq in cnt.items() if x + 1 in cnt)
# @lc code=end
