#
# @lc app=leetcode id=2433 lang=python3
#
# [2433] Find The Original Array of Prefix Xor
#
# https://leetcode.com/problems/find-the-original-array-of-prefix-xor/description/
#
# algorithms
# Medium (88.43%)
# Likes:    1528
# Dislikes: 92
# Total Accepted:    198K
# Total Submissions: 223.9K
# Testcase Example:  "[5,2,0,3,1]"
#
# You are given an integer array pref of size n. Find and return the array arr
# of size n that satisfies:
#
#
# pref[i] = arr[0] ^ arr[1] ^ ... ^ arr[i].
#
# Note that ^ denotes the bitwise-xor operation.
#
# It can be proven that the answer is unique.
#
#
#
# Example 1:
#
# Input: pref = [5,2,0,3,1]
# Output: [5,7,2,3,2]
# Explanation: From the array [5,7,2,3,2] we have the following:
# - pref[0] = 5.
# - pref[1] = 5 ^ 7 = 2.
# - pref[2] = 5 ^ 7 ^ 2 = 0.
# - pref[3] = 5 ^ 7 ^ 2 ^ 3 = 3.
# - pref[4] = 5 ^ 7 ^ 2 ^ 3 ^ 2 = 1.
#
# Example 2:
#
# Input: pref = [13]
# Output: [13]
# Explanation: We have pref[0] = arr[0] = 13.
#
#
#
# Constraints:
#
#
# 1 <= pref.length <= 10^5
#
#
# 0 <= pref[i] <= 10^6
#

# @lc code=start
from typing import List


class Solution:
    def findArray(self, pref: List[int]) -> List[int]:
        """
        Interview explanation:
        pref[i] = arr[0]^...^arr[i]. Recover arr.

        Algorithm:
        - arr[0]=pref[0]; arr[i]=pref[i]^pref[i-1].

        Complexity: O(n) time, O(n) space.
        """
        ans = [pref[0]]
        for i in range(1, len(pref)):
            ans.append(pref[i] ^ pref[i - 1])
        return ans

    def findArray_bit(self, pref: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate XOR reconstruction.

        Algorithm:
        - Same differences.

        Complexity: O(n) time, O(n) space.
        """
        return self.findArray(pref)
# @lc code=end
