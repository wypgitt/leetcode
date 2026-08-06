#
# @lc app=leetcode id=1224 lang=python3
#
# [1224] Maximum Equal Frequency
#
# https://leetcode.com/problems/maximum-equal-frequency/description/
#
# algorithms
# Hard (38.41%)
# Likes:    574
# Dislikes: 69
# Total Accepted:    20.1K
# Total Submissions: 52.4K
# Testcase Example:  "[2,2,1,1,5,3,3,5]"
#
# Given an array nums of positive integers, return the longest possible length
# of an array prefix of nums, such that it is possible to remove exactly one
# element from this prefix so that every number that has appeared in it will
# have the same number of occurrences.
#
# If after removing one element there are no remaining elements, it's still
# considered that every appeared number has the same number of ocurrences (0).
#
# Example 1:
#
# Input: nums = [2,2,1,1,5,3,3,5]
# Output: 7
# Explanation: For the subarray [2,2,1,1,5,3,3] of length 7, if we remove
# nums[4] = 5, we will get [2,2,1,1,3,3], so that each number will appear
# exactly twice.
#
# Example 2:
#
# Input: nums = [1,1,1,2,2,2,3,3,3,4,4,4,5]
# Output: 13
#
# Constraints:
#
# 2 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#


# @lc code=start
from typing import List
from collections import defaultdict

class Solution:
    def maxEqualFreq(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Longest prefix where we can remove one element so remaining all have
        equal frequency. Track count[val] and freq_of_freq; check valid patterns:
        (1) all unique, (2) one value appears once others equal, (3) one value
        appears freq+1 and others freq.

        Algorithm:
        - Maintain cnt, freq maps; after each insert check conditions; track max i

        Complexity: O(n) time, O(n) space.
        """
        cnt = defaultdict(int)
        freq = defaultdict(int)
        ans = 0
        for i, x in enumerate(nums, 1):
            if cnt[x]:
                freq[cnt[x]] -= 1
                if freq[cnt[x]] == 0:
                    del freq[cnt[x]]
            cnt[x] += 1
            freq[cnt[x]] += 1
            # valid if:
            # - one number total
            # - all freq 1
            # - one freq is 1 and only one such number, rest same
            # - max freq is F+1 for exactly one number, others F
            if len(cnt) == 1:
                ans = i
            elif len(freq) == 1:
                only = next(iter(freq))
                if only == 1:
                    ans = i
            elif len(freq) == 2:
                f1, f2 = sorted(freq.keys())
                if f1 == 1 and freq[1] == 1:
                    ans = i
                elif f2 == f1 + 1 and freq[f2] == 1:
                    ans = i
        return ans
# @lc code=end
