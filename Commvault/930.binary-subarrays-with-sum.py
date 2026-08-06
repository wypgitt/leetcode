#
# @lc app=leetcode id=930 lang=python3
#
# [930] Binary Subarrays With Sum
#
# https://leetcode.com/problems/binary-subarrays-with-sum/description/
#
# algorithms
# Medium (69.57%)
# Likes:    5004
# Dislikes: 173
# Total Accepted:    575K
# Total Submissions: 826K
# Testcase Example:  "[1,0,1,0,1]"
#
# Given a binary array nums and an integer goal, return the number of non-empty
# subarrays with a sum goal.
#
# A subarray is a contiguous part of the array.
#
# Example 1:
#
# Input: nums = [1,0,1,0,1], goal = 2
# Output: 4
# Explanation: The 4 subarrays are bolded and underlined below:
# [1,0,1,0,1]
# [1,0,1,0,1]
# [1,0,1,0,1]
# [1,0,1,0,1]
#
# Example 2:
#
# Input: nums = [0,0,0,0,0], goal = 0
# Output: 15
#
# Constraints:
#
# 1 <= nums.length <= 3 * 10^4
#
# nums[i] is either 0 or 1.
#
# 0 <= goal <= nums.length
#

# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def numSubarraysWithSum(self, nums: List[int], goal: int) -> int:
        """
        Interview explanation:
        Prefix-sum hash: count subarrays with sum == goal. For binary arrays,
        prefix[j] - prefix[i] = goal ⇒ number of prior prefixes equal to
        cur - goal.

        Algorithm (prefix hash):
        - freq={0:1}; cur=ans=0
        - For x in nums: cur += x; ans += freq[cur-goal]; freq[cur] += 1

        Complexity: O(n) time, O(n) space.
        """
        freq = defaultdict(int)
        freq[0] = 1
        cur = ans = 0
        for x in nums:
            cur += x
            ans += freq[cur - goal]
            freq[cur] += 1
        return ans

    def numSubarraysWithSum_atMost(self, nums: List[int], goal: int) -> int:
        """
        Interview explanation:
        Alternate classic optimal: sliding window atMost. For non-negative
        arrays, #sum==goal = atMost(goal) - atMost(goal-1).

        Algorithm (atMost sliding):
        - atMost(k): expand right adding nums[r]; while sum > k shrink left;
          each r contributes (r-l+1) subarrays ending at r with sum <= k
        - Return atMost(goal) - atMost(goal-1)

        Complexity: O(n) time, O(1) space.
        """
        def at_most(k: int) -> int:
            if k < 0:
                return 0
            left = s = ans = 0
            for right, x in enumerate(nums):
                s += x
                while s > k:
                    s -= nums[left]
                    left += 1
                ans += right - left + 1
            return ans

        return at_most(goal) - at_most(goal - 1)
# @lc code=end

