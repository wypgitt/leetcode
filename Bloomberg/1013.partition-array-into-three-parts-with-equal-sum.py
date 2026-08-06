#
# @lc app=leetcode id=1013 lang=python3
#
# [1013] Partition Array Into Three Parts With Equal Sum
#
# https://leetcode.com/problems/partition-array-into-three-parts-with-equal-sum/description/
#
# algorithms
# Easy (42.97%)
# Likes:    1820
# Dislikes: 169
# Total Accepted:    130K
# Total Submissions: 303K
# Testcase Example:  "[0,2,1,-6,6,-7,9,1,2,0,1]"
#
# Given an array of integers arr, return true if we can partition the array
# into three non-empty parts with equal sums.
#
# Formally, we can partition the array if we can find indexes i + 1 < j with
# (arr[0] + arr[1] + ... + arr[i] == arr[i + 1] + arr[i + 2] + ... + arr[j - 1]
# == arr[j] + arr[j + 1] + ... + arr[arr.length - 1])
#
# Example 1:
#
# Input: arr = [0,2,1,-6,6,-7,9,1,2,0,1]
# Output: true
# Explanation: 0 + 2 + 1 = -6 + 6 - 7 + 9 + 1 = 2 + 0 + 1
#
# Example 2:
#
# Input: arr = [0,2,1,-6,6,7,9,-1,2,0,1]
# Output: false
#
# Example 3:
#
# Input: arr = [3,3,6,5,-2,2,5,1,-9,4]
# Output: true
# Explanation: 3 + 3 = 6 = 5 - 2 + 2 + 5 + 1 - 9 + 4
#
# Constraints:
#
# 3 <= arr.length <= 5 * 10^4
#
# -10^4 <= arr[i] <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def canThreePartsEqualSum(self, arr: List[int]) -> bool:
        """
        Interview explanation:
        Total sum must be divisible by 3. Scan left-to-right accumulating; find
        first prefix equal to target, then a later prefix equal to 2*target,
        with remaining elements forming the third part (non-empty).

        Algorithm:
        - total = sum(arr); if total%3: False; target=total//3
        - Walk; count how many times running sum hits target (reset or count parts)
        - Need at least 3 parts (or 2 cuts leaving non-empty third)

        Complexity: O(n) time, O(1) space.
        """
        total = sum(arr)
        if total % 3 != 0:
            return False
        target = total // 3
        parts = running = 0
        for i, x in enumerate(arr):
            running += x
            if running == target:
                parts += 1
                running = 0
                if parts == 2 and i < len(arr) - 1:
                    return True
        return False
# @lc code=end
