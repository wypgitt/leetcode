#
# @lc app=leetcode id=560 lang=python3
#
# [560] Subarray Sum Equals K
#
# https://leetcode.com/problems/subarray-sum-equals-k/description/
#
# algorithms
# Medium (47.9%)
# Likes:    25547
# Dislikes: 862
# Total Accepted:    2.6M
# Total Submissions: 5.5M
# Testcase Example:  "[1,1,1]"
#
# Given an array of integers nums and an integer k, return the total number of
# subarrays whose sum equals to k.
#
# A subarray is a contiguous non-empty sequence of elements within an array.
#
# Example 1:
#
# Input: nums = [1,1,1], k = 2
# Output: 2
#
# Example 2:
#
# Input: nums = [1,2,3], k = 3
# Output: 2
#
# Constraints:
#
# 1 <= nums.length <= 2 * 10^4
#
# -1000 <= nums[i] <= 1000
#
# -10^7 <= k <= 10^7
#

# @lc code=start
from collections import defaultdict
from typing import List
class Solution:
    def subarraySum(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Prefix-sum + hashmap: count of subarrays ending here with sum k equals
        how many earlier prefixes equal current_prefix - k.

        Algorithm:
        - freq[0] = 1; walk prefix; ans += freq[prefix - k]; freq[prefix] += 1.

        Complexity: O(n) time, O(n) space.
        """
        freq = defaultdict(int)
        freq[0] = 1
        prefix = ans = 0
        for x in nums:
            prefix += x
            ans += freq[prefix - k]
            freq[prefix] += 1
        return ans
# @lc code=end

