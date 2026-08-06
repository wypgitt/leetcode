#
# @lc app=leetcode id=1385 lang=python3
#
# [1385] Find the Distance Value Between Two Arrays
#
# https://leetcode.com/problems/find-the-distance-value-between-two-arrays/description/
#
# algorithms
# Easy (72.11%)
# Likes:    1044
# Dislikes: 3176
# Total Accepted:    155K
# Total Submissions: 216K
# Testcase Example:  "[4,5,8]"
#
# Given two integer arrays arr1 and arr2, and the integer d, return the
# distance value between the two arrays.
#
# The distance value is defined as the number of elements arr1[i] such that
# there is not any element arr2[j] where |arr1[i]-arr2[j]| <= d.
#
# Example 1:
#
# Input: arr1 = [4,5,8], arr2 = [10,9,1,8], d = 2
# Output: 2
# Explanation:
# For arr1[0]=4 we have:
# |4-10|=6 > d=2
# |4-9|=5 > d=2
# |4-1|=3 > d=2
# |4-8|=4 > d=2
# For arr1[1]=5 we have:
# |5-10|=5 > d=2
# |5-9|=4 > d=2
# |5-1|=4 > d=2
# |5-8|=3 > d=2
# For arr1[2]=8 we have:
# |8-10|=2 <= d=2
# |8-9|=1 <= d=2
# |8-1|=7 > d=2
# |8-8|=0 <= d=2
#
# Example 2:
#
# Input: arr1 = [1,4,2,3], arr2 = [-4,-3,6,10,20,30], d = 3
# Output: 2
#
# Example 3:
#
# Input: arr1 = [2,1,100,3], arr2 = [-5,-2,10,-3,7], d = 6
# Output: 1
#
# Constraints:
#
# 1 <= arr1.length, arr2.length <= 500
#
# -1000 <= arr1[i], arr2[j] <= 1000
#
# 0 <= d <= 100
#

# @lc code=start

from typing import List
import bisect


class Solution:
    def findTheDistanceValue(self, arr1: List[int], arr2: List[int], d: int) -> int:
        """
        Interview explanation:
        Count elements of arr1 such that all arr2 elements are >d away.
        Sort arr2; for each a binary-search nearest and check distance.

        Algorithm:
        - Sort arr2; for a in arr1: find insertion; check neighbors vs d

        Complexity: O((n+m) log m) time, O(m) space if copy.
        """
        arr2 = sorted(arr2)
        ans = 0
        for a in arr1:
            i = bisect.bisect_left(arr2, a)
            ok = True
            if i < len(arr2) and abs(arr2[i] - a) <= d:
                ok = False
            if i > 0 and abs(arr2[i - 1] - a) <= d:
                ok = False
            if ok:
                ans += 1
        return ans

    def findTheDistanceValue_brute(self, arr1: List[int], arr2: List[int], d: int) -> int:
        """
        Interview explanation:
        Alternate brute force pairwise distance check.

        Algorithm:
        - For each a: all(abs(a-b)>d for b in arr2)

        Complexity: O(n*m) time, O(1) space.
        """
        return sum(all(abs(a - b) > d for b in arr2) for a in arr1)
# @lc code=end
