#
# @lc app=leetcode id=3834 lang=python3
#
# [3834] Merge Adjacent Equal Elements
#
# https://leetcode.com/problems/merge-adjacent-equal-elements/description/
#
# algorithms
# Medium (42.61%)
# Likes:    96
# Dislikes: 2
# Total Accepted:    46.9K
# Total Submissions: 110.1K
# Testcase Example:  "[3,1,1,2]"
#
#
# You are given an integer array nums.
#
# You must repeatedly apply the following merge operation until no more
# changes can be made:
#
# If any two adjacent elements are equal, choose the leftmost such
# adjacent pair in the current array and replace them with a single
# element equal to their sum.
#
# After each merge operation, the array size decreases by 1. Repeat the
# process on the updated array until no more changes can be made.
#
# Return the final array after all possible merge operations.
#
# Example 1:
#
# Input: nums = [3,1,1,2]
#
# Output: [3,4]
#
# Explanation:
#
# The middle two elements are equal and merged into 1 + 1 = 2, resulting
# in [3, 2, 2].
#
# The last two elements are equal and merged into 2 + 2 = 4, resulting in
# [3, 4].
#
# No adjacent equal elements remain. Thus, the answer is [3, 4].
#
# Example 2:
#
# Input: nums = [2,2,4]
#
# Output: [8]
#
# Explanation:
#
# The first two elements are equal and merged into 2 + 2 = 4, resulting in
# [4, 4].
#
# The first two elements are equal and merged into 4 + 4 = 8, resulting in
# [8].
#
# Example 3:
#
# Input: nums = [3,7,5]
#
# Output: [3,7,5]
#
# Explanation:
#
# There are no adjacent equal elements in the array, so no operations are
# performed.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5​​​​​​​
#

# @lc code=start
from typing import List


class Solution:
    def mergeAdjacent(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Repeatedly replace the leftmost adjacent equal pair with their sum
        until no adjacent equals remain. A stack that eagerly merges equals
        simulates the cascade correctly.

        Algorithm:
        - Push each value; while top two are equal, pop both and push sum.

        Complexity: O(n) time, O(n) space.
        """
        stk: List[int] = []
        for x in nums:
            stk.append(x)
            while len(stk) > 1 and stk[-1] == stk[-2]:
                stk.append(stk.pop() + stk.pop())
        return stk
# @lc code=end
