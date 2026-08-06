#
# @lc app=leetcode id=3101 lang=python3
#
# [3101] Count Alternating Subarrays
#
# https://leetcode.com/problems/count-alternating-subarrays/description/
#
# algorithms
# Medium (57.56%)
# Likes:    251
# Dislikes: 10
# Total Accepted:    46.7K
# Total Submissions: 81.1K
# Testcase Example:  "[0,1,1,1]"
#
#
# You are given a binary array nums.
#
# We call a subarray alternating if no two adjacent elements in the
# subarray have the same value.
#
# Return the number of alternating subarrays in nums.
#
# Example 1:
#
# Input: nums = [0,1,1,1]
#
# Output: 5
#
# Explanation:
#
# The following subarrays are alternating: [0], [1], [1], [1], and [0,1].
#
# Example 2:
#
# Input: nums = [1,0,1,0]
#
# Output: 10
#
# Explanation:
#
# Every subarray of the array is alternating. There are 10 possible
# subarrays that we can choose.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# nums[i] is either 0 or 1.
#

# @lc code=start
from typing import List


class Solution:
    def countAlternatingSubarrays(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Count subarrays with no two equal adjacent bits.

        Algorithm:
        - Track length of alternating run ending at i; each ending contributes
          that length new subarrays. Reset run when equal neighbors appear.

        Complexity: O(n) time, O(1) space.
        """
        ans = 1
        length = 1
        for i in range(1, len(nums)):
            if nums[i] != nums[i - 1]:
                length += 1
            else:
                length = 1
            ans += length
        return ans
# @lc code=end
