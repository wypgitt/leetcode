#
# @lc app=leetcode id=2007 lang=python3
#
# [2007] Find Original Array From Doubled Array
#
# https://leetcode.com/problems/find-original-array-from-doubled-array/description/
#
# algorithms
# Medium (40.89%)
# Likes:    2583
# Dislikes: 120
# Total Accepted:    158.9K
# Total Submissions: 388.5K
# Testcase Example:  "[1,3,4,2,6,8]"
#
# An integer array original is transformed into a doubled array changed by
# appending twice the value of every element in original, and then randomly
# shuffling the resulting array.
#
# Given an array changed, return original if changed is a doubled array. If
# changed is not a doubled array, return an empty array. The elements in
# original may be returned in any order.
#
#
#
# Example 1:
#
# Input: changed = [1,3,4,2,6,8]
# Output: [1,3,4]
# Explanation: One possible original array could be [1,3,4]:
# - Twice the value of 1 is 1 * 2 = 2.
# - Twice the value of 3 is 3 * 2 = 6.
# - Twice the value of 4 is 4 * 2 = 8.
# Other original arrays could be [4,3,1] or [3,1,4].
#
# Example 2:
#
# Input: changed = [6,3,0,1]
# Output: []
# Explanation: changed is not a doubled array.
#
# Example 3:
#
# Input: changed = [1]
# Output: []
# Explanation: changed is not a doubled array.
#
#
#
# Constraints:
#
#
# 1 <= changed.length <= 10^5
#
#
# 0 <= changed[i] <= 10^5
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def findOriginalArray(self, changed: List[int]) -> List[int]:
        """
        Interview explanation:
        changed is concatenation of original and each element doubled (any order).
        Recover original or [] if impossible.

        Algorithm:
        - Sort; greedily match each unused x with 2x via Counter (handle 0 specially).

        Complexity: O(n log n) time, O(n) space.
        """
        if len(changed) % 2:
            return []
        changed.sort()
        cnt = Counter(changed)
        ans = []
        for x in changed:
            if cnt[x] == 0:
                continue
            cnt[x] -= 1
            if cnt[2 * x] == 0:
                return []
            cnt[2 * x] -= 1
            ans.append(x)
        return ans
# @lc code=end
