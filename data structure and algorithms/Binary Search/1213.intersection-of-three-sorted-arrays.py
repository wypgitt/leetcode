#
# @lc app=leetcode id=1213 lang=python3
#
# [1213] Intersection of Three Sorted Arrays
#
# https://leetcode.com/problems/intersection-of-three-sorted-arrays/description/
#
# algorithms
# Easy (79.99%)
# Likes:    616
# Dislikes: 26
# Total Accepted:    103.6K
# Total Submissions: 129.6K
# Testcase Example:  "[1,2,3,4,5]\n[1,2,5,7,9]\n[1,3,4,5,8]"
#
#
# Given three integer arrays arr1, arr2 and arr3 sorted in strictly
# increasing order, return a sorted array of only the integers that
# appeared in all three arrays.
#
# Example 1:
#
# Input: arr1 = [1,2,3,4,5], arr2 = [1,2,5,7,9], arr3 = [1,3,4,5,8]
# Output: [1,5]
# Explanation: Only 1 and 5 appeared in the three arrays.
#
# Example 2:
#
# Input: arr1 = [197,418,523,876,1356], arr2 = [501,880,1593,1710,1870],
# arr3 = [521,682,1337,1395,1764]
# Output: []
#
# Constraints:
#
# 1 <= arr1.length, arr2.length, arr3.length <= 1000
#
# 1 <= arr1[i], arr2[i], arr3[i] <= 2000
#
# @lc code=start
from typing import List

class Solution:
    def arraysIntersection(self, arr1: List[int], arr2: List[int], arr3: List[int]) -> List[int]:
        """
        Interview explanation:
        Premium. Three sorted arrays; return common elements in sorted order.
        Three-pointer advance the smallest; when all equal emit and advance all.

        Algorithm:
        - i=j=k=0; while all in range: if equal append & ++all; else ++ the min

        Complexity: O(n) time, O(1) extra (output aside).
        """
        i = j = k = 0
        ans = []
        while i < len(arr1) and j < len(arr2) and k < len(arr3):
            a, b, c = arr1[i], arr2[j], arr3[k]
            if a == b == c:
                ans.append(a)
                i += 1
                j += 1
                k += 1
            else:
                m = min(a, b, c)
                if a == m:
                    i += 1
                if b == m:
                    j += 1
                if c == m:
                    k += 1
        return ans

    def arraysIntersection_set(self, arr1: List[int], arr2: List[int], arr3: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate: set intersection of the three arrays; sort result.

        Algorithm:
        - sorted(set(arr1) & set(arr2) & set(arr3))

        Complexity: O(n log n) time, O(n) space.
        """
        return sorted(set(arr1) & set(arr2) & set(arr3))
# @lc code=end
