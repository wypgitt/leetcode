#
# @lc app=leetcode id=3837 lang=python3
#
# [3837] Delayed Count of Equal Elements
#
# https://leetcode.com/problems/delayed-count-of-equal-elements/description/
#
# algorithms
# Medium (78.29%)
# Likes:    5
# Dislikes: 2
# Total Accepted:    548
# Total Submissions: 700
# Testcase Example:  "[1,2,1,1]\n1"
#
#
# You are given an integer array nums of length n and an integer k.
#
# For each index i, define the delayed count as the number of indices j
# such that:
#
# i + k < j <= n - 1, and
#
# nums[j] == nums[i]
#
# Return an array ans where ans[i] is the delayed count of index i.
#
# Example 1:
#
# Input: nums = [1,2,1,1], k = 1
#
# Output: [2,0,0,0]
#
# Explanation:
#
#                         i
#                         nums[i]
#                         possible j
#                         nums[j]
#                         satisfying
#
#                         nums[j] == nums[i]
#                         ans[i]
#
#                         0
#                         1
#                         [2, 3]
#                         [1, 1]
#                         [2, 3]
#                         2
#
#                         1
#                         2
#                         [3]
#                         [1]
#                         []
#                         0
#
#                         2
#                         1
#                         []
#                         []
#                         []
#                         0
#
#                         3
#                         1
#                         []
#                         []
#                         []
#                         0
#
# Thus, ans = [2, 0, 0, 0]​​​​​​​.
#
# Example 2:
#
# Input: nums = [3,1,3,1], k = 0
#
# Output: [1,1,0,0]
#
# Explanation:
#
#                         i
#                         nums[i]
#                         possible j
#                         nums[j]
#                         satisfying
#
#                         nums[j] == nums[i]
#                         ans[i]
#
#                         0
#                         3
#                         [1, 2, 3]
#                         [1, 3, 1]
#                         [2]
#                         1
#
#                         1
#                         1
#                         [2, 3]
#                         [3, 1]
#                         [3]
#                         1
#
#                         2
#                         3
#                         [3]
#                         [1]
#                         []
#                         0
#
#                         3
#                         1
#                         []
#                         []
#                         []
#                         0
#
# Thus, ans = [1, 1, 0, 0]​​​​​​​.
#
# Constraints:
#
# 1 <= n == nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#
# 0 <= k <= n - 1
#

# @lc code=start
from collections import Counter
from typing import List


class Solution:
    def delayedCount(self, nums: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        For each i, count later indices j > i + k with the same value.

        Algorithm:
        - Scan i from right to left starting at n-k-2.
        - Before answering i, add nums[i+k+1] into a frequency map.
        - ans[i] = frequency of nums[i] among already-added positions.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        cnt: Counter = Counter()
        ans = [0] * n
        for i in range(n - k - 2, -1, -1):
            cnt[nums[i + k + 1]] += 1
            ans[i] = cnt[nums[i]]
        return ans
# @lc code=end
