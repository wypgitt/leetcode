#
# @lc app=leetcode id=2364 lang=python3
#
# [2364] Count Number of Bad Pairs
#
# https://leetcode.com/problems/count-number-of-bad-pairs/description/
#
# algorithms
# Medium (54.13%)
# Likes:    1811
# Dislikes: 62
# Total Accepted:    189.4K
# Total Submissions: 349.9K
# Testcase Example:  "[4,1,3,3]"
#
# You are given a 0-indexed integer array nums. A pair of indices (i, j) is a
# bad pair if i < j and j - i != nums[j] - nums[i].
#
# Return the total number of bad pairs in nums.
#
#
#
# Example 1:
#
# Input: nums = [4,1,3,3]
# Output: 5
# Explanation: The pair (0, 1) is a bad pair since 1 - 0 != 1 - 4.
# The pair (0, 2) is a bad pair since 2 - 0 != 3 - 4, 2 != -1.
# The pair (0, 3) is a bad pair since 3 - 0 != 3 - 4, 3 != -1.
# The pair (1, 2) is a bad pair since 2 - 1 != 3 - 1, 1 != 2.
# The pair (2, 3) is a bad pair since 3 - 2 != 3 - 3, 1 != 0.
# There are a total of 5 bad pairs, so we return 5.
#
# Example 2:
#
# Input: nums = [1,2,3,4,5]
# Output: 0
# Explanation: There are no bad pairs.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start

from typing import List
from collections import Counter


class Solution:
    def countBadPairs(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Bad pair (i,j) i<j if j-i != nums[j]-nums[i], i.e. nums[i]-i !=
        nums[j]-j. Count bad = total pairs - good pairs.

        Algorithm:
        - Hash count of (nums[i]-i); good = sum c*(c-1)/2; ans = n*(n-1)/2 - good.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        cnt = Counter(x - i for i, x in enumerate(nums))
        good = sum(c * (c - 1) // 2 for c in cnt.values())
        return n * (n - 1) // 2 - good
# @lc code=end
