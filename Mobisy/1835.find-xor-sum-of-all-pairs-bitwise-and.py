#
# @lc app=leetcode id=1835 lang=python3
#
# [1835] Find XOR Sum of All Pairs Bitwise AND
#
# https://leetcode.com/problems/find-xor-sum-of-all-pairs-bitwise-and/description/
#
# algorithms
# Hard (62.74%)
# Likes:    634
# Dislikes: 51
# Total Accepted:    27.7K
# Total Submissions: 44.2K
# Testcase Example:  "[1,2,3]"
#
# The XOR sum of a list is the bitwise XOR of all its elements. If the list
# only contains one element, then its XOR sum will be equal to this element.
#
# For example, the XOR sum of [1,2,3,4] is equal to 1 XOR 2 XOR 3 XOR 4 = 4,
# and the XOR sum of [3] is equal to 3.
#
# You are given two 0-indexed arrays arr1 and arr2 that consist only of
# non-negative integers.
#
# Consider the list containing the result of arr1[i] AND arr2[j] (bitwise AND)
# for every (i, j) pair where 0 <= i < arr1.length and 0 <= j < arr2.length.
#
# Return the XOR sum of the aforementioned list.
#
# Example 1:
#
# Input: arr1 = [1,2,3], arr2 = [6,5]
# Output: 0
# Explanation: The list = [1 AND 6, 1 AND 5, 2 AND 6, 2 AND 5, 3 AND 6, 3 AND
# 5] = [0,1,2,0,2,1].
# The XOR sum = 0 XOR 1 XOR 2 XOR 0 XOR 2 XOR 1 = 0.
#
# Example 2:
#
# Input: arr1 = [12], arr2 = [4]
# Output: 4
# Explanation: The list = [12 AND 4] = [4]. The XOR sum = 4.
#
# Constraints:
#
# 1 <= arr1.length, arr2.length <= 10^5
#
# 0 <= arr1[i], arr2[j] <= 10^9
#

# @lc code=start
from typing import List
from functools import reduce
import operator


class Solution:
    def getXORSum(self, arr1: List[int], arr2: List[int]) -> int:
        """
        Interview explanation:
        XOR of all (a&b) for a in arr1, b in arr2. Since XOR of ANDs distributes:
        (a1&b1)^(a1&b2)^... = a1 & (b1^b2^...) and overall =
        (XOR of all arr1) & (XOR of all arr2).

        Algorithm (XOR property):
        - return xor(arr1) & xor(arr2).

        Complexity: O(n+m) time, O(1) space.
        """
        x1 = 0
        for a in arr1:
            x1 ^= a
        x2 = 0
        for b in arr2:
            x2 ^= b
        return x1 & x2
# @lc code=end
