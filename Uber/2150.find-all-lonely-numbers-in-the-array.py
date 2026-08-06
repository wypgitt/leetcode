#
# @lc app=leetcode id=2150 lang=python3
#
# [2150] Find All Lonely Numbers in the Array
#
# https://leetcode.com/problems/find-all-lonely-numbers-in-the-array/description/
#
# algorithms
# Medium (63.73%)
# Likes:    718
# Dislikes: 67
# Total Accepted:    77.5K
# Total Submissions: 121.6K
# Testcase Example:  "[10,6,5,8]"
#
# You are given an integer array nums. A number x is lonely when it appears only
# once, and no adjacent numbers (i.e. x + 1 and x - 1) appear in the array.
#
# Return all lonely numbers in nums. You may return the answer in any order.
#
#
#
# Example 1:
#
# Input: nums = [10,6,5,8]
# Output: [10,8]
# Explanation:
# - 10 is a lonely number since it appears exactly once and 9 and 11 does not
# appear in nums.
# - 8 is a lonely number since it appears exactly once and 7 and 9 does not
# appear in nums.
# - 5 is not a lonely number since 6 appears in nums and vice versa.
# Hence, the lonely numbers in nums are [10, 8].
# Note that [8, 10] may also be returned.
#
# Example 2:
#
# Input: nums = [1,3,5,3]
# Output: [1,5]
# Explanation:
# - 1 is a lonely number since it appears exactly once and 0 and 2 does not
# appear in nums.
# - 5 is a lonely number since it appears exactly once and 4 and 6 does not
# appear in nums.
# - 3 is not a lonely number since it appears twice.
# Hence, the lonely numbers in nums are [1, 5].
# Note that [5, 1] may also be returned.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 0 <= nums[i] <= 10^6
#


# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def findLonely(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Lonely = appears exactly once and neither x-1 nor x+1 appears.

        Algorithm:
        - Frequency map; filter.

        Complexity: O(n) time, O(n) space.
        """
        cnt = Counter(nums)
        return [x for x, c in cnt.items() if c == 1 and (x - 1) not in cnt and (x + 1) not in cnt]
# @lc code=end

