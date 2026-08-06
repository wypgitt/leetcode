#
# @lc app=leetcode id=2216 lang=python3
#
# [2216] Minimum Deletions to Make Array Beautiful
#
# https://leetcode.com/problems/minimum-deletions-to-make-array-beautiful/description/
#
# algorithms
# Medium (50.27%)
# Likes:    844
# Dislikes: 96
# Total Accepted:    41.9K
# Total Submissions: 83.4K
# Testcase Example:  "[1,1,2,3,5]"
#
# You are given a 0-indexed integer array nums. The array nums is beautiful if:
#
#
# nums.length is even.
#
#
# nums[i] != nums[i + 1] for all i % 2 == 0.
#
# Note that an empty array is considered beautiful.
#
# You can delete any number of elements from nums. When you delete an element,
# all the elements to the right of the deleted element will be shifted one unit
# to the left to fill the gap created and all the elements to the left of the
# deleted element will remain unchanged.
#
# Return the minimum number of elements to delete from nums to make it
# beautiful.
#
#
#
# Example 1:
#
# Input: nums = [1,1,2,3,5]
# Output: 1
# Explanation: You can delete either nums[0] or nums[1] to make nums = [1,2,3,5]
# which is beautiful. It can be proven you need at least 1 deletion to make nums
# beautiful.
#
# Example 2:
#
# Input: nums = [1,1,2,2,3,3]
# Output: 2
# Explanation: You can delete nums[0] and nums[5] to make nums = [1,2,2,3] which
# is beautiful. It can be proven you need at least 2 deletions to make nums
# beautiful.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 0 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def minDeletion(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Array beautiful if even length and nums[i]!=nums[i+1] for every even i.
        Min deletions to make beautiful.

        Algorithm:
        - Greedy: walk keeping a parity for next even index; delete when equal
          pair would form; if final length odd delete last.

        Complexity: O(n) time, O(1) space.
        """
        deletions = 0
        prev = None
        kept = 0
        for x in nums:
            if kept % 2 == 0:
                prev = x
                kept += 1
            else:
                if x == prev:
                    deletions += 1
                else:
                    kept += 1
        if kept % 2 == 1:
            deletions += 1
        return deletions
# @lc code=end
