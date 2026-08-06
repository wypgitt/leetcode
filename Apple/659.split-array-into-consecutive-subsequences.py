#
# @lc app=leetcode id=659 lang=python3
#
# [659] Split Array into Consecutive Subsequences
#
# https://leetcode.com/problems/split-array-into-consecutive-subsequences/description/
#
# algorithms
# Medium (52.41%)
# Likes:    4601
# Dislikes: 817
# Total Accepted:    152K
# Total Submissions: 291K
# Testcase Example:  "[1,2,3,3,4,5]"
#
# You are given an integer array nums that is sorted in non-decreasing order.
#
# Determine if it is possible to split nums into one or more subsequences such
# that both of the following conditions are true:
#
# Each subsequence is a consecutive increasing sequence (i.e. each integer is
# exactly one more than the previous integer).
#
# All subsequences have a length of 3 or more.
#
# Return true if you can split nums according to the above conditions, or false
# otherwise.
#
# A subsequence of an array is a new array that is formed from the original
# array by deleting some (can be none) of the elements without disturbing the
# relative positions of the remaining elements. (i.e., [1,3,5] is a subsequence
# of [1,2,3,4,5] while [1,3,2] is not).
#
# Example 1:
#
# Input: nums = [1,2,3,3,4,5]
# Output: true
# Explanation: nums can be split into the following subsequences:
# [1,2,3,3,4,5] --> 1, 2, 3
# [1,2,3,3,4,5] --> 3, 4, 5
#
# Example 2:
#
# Input: nums = [1,2,3,3,4,4,5,5]
# Output: true
# Explanation: nums can be split into the following subsequences:
# [1,2,3,3,4,4,5,5] --> 1, 2, 3, 4, 5
# [1,2,3,3,4,4,5,5] --> 3, 4, 5
#
# Example 3:
#
# Input: nums = [1,2,3,4,4,5]
# Output: false
# Explanation: It is impossible to split nums into consecutive increasing
# subsequences of length 3 or more.
#
# Constraints:
#
# 1 <= nums.length <= 10^4
#
# -1000 <= nums[i] <= 1000
#
# nums is sorted in non-decreasing order.
#

# @lc code=start

from collections import Counter
from typing import List


class Solution:
    def isPossible(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Split into consecutive subsequences of length >= 3. Greedy: prefer
        appending to an existing chain ending at x-1; else start a new chain
        x,x+1,x+2 if freqs allow.

        Algorithm:
        - freq Counter; tails Counter of chains ending at value.
        - For each x: if freq[x]==0 continue; elif tails[x-1]>0: extend;
          elif freq[x+1] and freq[x+2]: start new; else False.

        Complexity: O(N) time, O(U) space.
        """
        freq = Counter(nums)
        tails = Counter()
        for x in nums:
            if freq[x] == 0:
                continue
            freq[x] -= 1
            if tails[x - 1] > 0:
                tails[x - 1] -= 1
                tails[x] += 1
            elif freq[x + 1] > 0 and freq[x + 2] > 0:
                freq[x + 1] -= 1
                freq[x + 2] -= 1
                tails[x + 2] += 1
            else:
                return False
        return True
# @lc code=end
