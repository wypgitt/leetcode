#
# @lc app=leetcode id=1346 lang=python3
#
# [1346] Check If N and Its Double Exist
#
# https://leetcode.com/problems/check-if-n-and-its-double-exist/description/
#
# algorithms
# Easy (41.95%)
# Likes:    2546
# Dislikes: 259
# Total Accepted:    648K
# Total Submissions: 1.5M
# Testcase Example:  "[10,2,5,3]"
#
# Given an array arr of integers, check if there exist two indices i and j such
# that :
#
# i != j
#
# 0 <= i, j < arr.length
#
# arr[i] == 2 * arr[j]
#
# Example 1:
#
# Input: arr = [10,2,5,3]
# Output: true
# Explanation: For i = 0 and j = 2, arr[i] == 10 == 2 * 5 == 2 * arr[j]
#
# Example 2:
#
# Input: arr = [3,1,7,11]
# Output: false
# Explanation: There is no i and j that satisfy the conditions.
#
# Constraints:
#
# 2 <= arr.length <= 500
#
# -10^3 <= arr[i] <= 10^3
#

# @lc code=start
from typing import List


class Solution:
    def checkIfExist(self, arr: List[int]) -> bool:
        """
        Interview explanation:
        Exists i!=j with arr[i]==2*arr[j]. Hash set while scanning: check
        2*x and x/2 (if even) against seen.

        Algorithm:
        - seen set; for x: if 2x in seen or (x even and x//2 in seen); add x.

        Complexity: O(n) time, O(n) space.
        """
        seen = set()
        for x in arr:
            if 2 * x in seen or (x % 2 == 0 and x // 2 in seen):
                return True
            seen.add(x)
        return False

    def checkIfExist_sort(self, arr: List[int]) -> bool:
        """
        Interview explanation:
        Alternate: sort + two pointers / binary search for 2*arr[i].

        Algorithm:
        - Sort; for each i bisect 2*arr[i] with different index.

        Complexity: O(n log n) time, O(n) or O(1) extra.
        """
        import bisect
        a = sorted(arr)
        for i, x in enumerate(a):
            j = bisect.bisect_left(a, 2 * x)
            if j < len(a) and a[j] == 2 * x and j != i:
                return True
        return False
# @lc code=end

