#
# @lc app=leetcode id=1356 lang=python3
#
# [1356] Sort Integers by The Number of 1 Bits
#
# https://leetcode.com/problems/sort-integers-by-the-number-of-1-bits/description/
#
# algorithms
# Easy (82.43%)
# Likes:    2877
# Dislikes: 138
# Total Accepted:    404K
# Total Submissions: 490K
# Testcase Example:  "[0,1,2,3,4,5,6,7,8]"
#
# You are given an integer array arr. Sort the integers in the array in
# ascending order by the number of 1's in their binary representation and in
# case of two or more integers have the same number of 1's you have to sort
# them in ascending order.
#
# Return the array after sorting it.
#
# Example 1:
#
# Input: arr = [0,1,2,3,4,5,6,7,8]
# Output: [0,1,2,4,8,3,5,6,7]
# Explantion: [0] is the only integer with 0 bits.
# [1,2,4,8] all have 1 bit.
# [3,5,6] have 2 bits.
# [7] has 3 bits.
# The sorted array by bits is [0,1,2,4,8,3,5,6,7]
#
# Example 2:
#
# Input: arr = [1024,512,256,128,64,32,16,8,4,2,1]
# Output: [1,2,4,8,16,32,64,128,256,512,1024]
# Explantion: All integers have 1 bit in the binary representation, you should
# just sort them in ascending order.
#
# Constraints:
#
# 1 <= arr.length <= 500
#
# 0 <= arr[i] <= 10^4
#

# @lc code=start

from typing import List


class Solution:
    def sortByBits(self, arr: List[int]) -> List[int]:
        """
        Interview explanation:
        Sort by popcount ascending, then by value ascending.

        Algorithm:
        - sorted(arr, key=lambda x: (bin(x).count('1'), x))

        Complexity: O(n log n) time, O(n) space.
        """
        return sorted(arr, key=lambda x: (bin(x).count("1"), x))

    def sortByBits_builtin(self, arr: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate using int.bit_count() for popcount.

        Algorithm:
        - sorted(arr, key=lambda x: (x.bit_count(), x))

        Complexity: O(n log n) time, O(n) space.
        """
        return sorted(arr, key=lambda x: (x.bit_count(), x))
# @lc code=end
