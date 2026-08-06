#
# @lc app=leetcode id=1546 lang=python3
#
# [1546] Maximum Number of Non-Overlapping Subarrays With Sum Equals Target
#
# https://leetcode.com/problems/maximum-number-of-non-overlapping-subarrays-with-sum-equals-target/description/
#
# algorithms
# Medium (49.17%)
# Likes:    1128
# Dislikes: 27
# Total Accepted:    37.0K
# Total Submissions: 75.3K
# Testcase Example:  "[1,1,1,1,1]"
#
# Given an array nums and an integer target, return the maximum number of
# non-empty non-overlapping subarrays such that the sum of values in each
# subarray is equal to target.
#
# Example 1:
#
# Input: nums = [1,1,1,1,1], target = 2
# Output: 2
# Explanation: There are 2 non-overlapping subarrays [1,1,1,1,1] with sum
# equals to target(2).
#
# Example 2:
#
# Input: nums = [-1,3,5,1,4,2,-9], target = 6
# Output: 2
# Explanation: There are 3 subarrays with sum equal to 6.
# ([5,1], [4,2], [3,5,1,4,2,-9]) but only the first 2 are non-overlapping.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^4 <= nums[i] <= 10^4
#
# 0 <= target <= 10^6
#

# @lc code=start
from typing import List


class Solution:
    def maxNonOverlapping(self, nums: List[int], target: int) -> int:
        """
        Interview explanation:
        Max number of non-overlapping subarrays with sum==target. Greedy:
        take earliest-ending valid subarray each time (prefix sum + set of
        sums since last taken end).

        Algorithm:
        - seen={0}; pref=0; ans=0; for x: pref+=x; if pref-target in seen:
          ans++; seen={0}; pref=0; else seen.add(pref).

        Complexity: O(n) time, O(n) space.
        """
        seen = {0}
        pref = 0
        ans = 0
        for x in nums:
            pref += x
            if pref - target in seen:
                ans += 1
                seen = {0}
                pref = 0
            else:
                seen.add(pref)
        return ans
# @lc code=end
