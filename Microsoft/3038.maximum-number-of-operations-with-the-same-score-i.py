#
# @lc app=leetcode id=3038 lang=python3
#
# [3038] Maximum Number of Operations With the Same Score I
#
# https://leetcode.com/problems/maximum-number-of-operations-with-the-same-score-i/description/
#
# algorithms
# Easy (52.86%)
# Likes:    97
# Dislikes: 29
# Total Accepted:    43K
# Total Submissions: 81.4K
# Testcase Example:  "[3,2,1,4,5]"
#
#
# You are given an array of integers nums. Consider the following
# operation:
#
# Delete the first two elements nums and define the score of the operation
# as the sum of these two elements.
#
# You can perform this operation until nums contains fewer than two
# elements. Additionally, the same score must be achieved in all
# operations.
#
# Return the maximum number of operations you can perform.
#
# Example 1:
#
# Input: nums = [3,2,1,4,5]
#
# Output: 2
#
# Explanation:
#
# We can perform the first operation with the score 3 + 2 = 5. After this
# operation, nums = [1,4,5].
#
# We can perform the second operation as its score is 4 + 1 = 5, the same
# as the previous operation. After this operation, nums = [5].
#
# As there are fewer than two elements, we can't perform more operations.
#
# Example 2:
#
# Input: nums = [1,5,3,3,4,1,3,2,2,3]
#
# Output: 2
#
# Explanation:
#
# We can perform the first operation with the score 1 + 5 = 6. After this
# operation, nums = [3,3,4,1,3,2,2,3].
#
# We can perform the second operation as its score is 3 + 3 = 6, the same
# as the previous operation. After this operation, nums = [4,1,3,2,2,3].
#
# We cannot perform the next operation as its score is 4 + 1 = 5, which is
# different from the previous scores.
#
# Example 3:
#
# Input: nums = [5,3]
#
# Output: 1
#
# Constraints:
#
# 2 <= nums.length <= 100
#
# 1 <= nums[i] <= 1000
#

# @lc code=start

from typing import List


class Solution:
    def maxOperations(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Only the prefix can be deleted, two at a time, and every operation
        must share the first operation's score.

        Algorithm:
        - score = nums[0]+nums[1]; keep taking next pairs while sum == score.

        Complexity: O(n) time, O(1) space.
        """
        score = nums[0] + nums[1]
        ans = 1
        i = 2
        while i + 1 < len(nums) and nums[i] + nums[i + 1] == score:
            ans += 1
            i += 2
        return ans
# @lc code=end
