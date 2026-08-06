#
# @lc app=leetcode id=992 lang=python3
#
# [992] Subarrays with K Different Integers
#
# https://leetcode.com/problems/subarrays-with-k-different-integers/description/
#
# algorithms
# Hard (68.78%)
# Likes:    7088
# Dislikes: 126
# Total Accepted:    438K
# Total Submissions: 637K
# Testcase Example:  "[1,2,1,2,3]"
#
# Given an integer array nums and an integer k, return the number of good
# subarrays of nums.
#
# A good array is an array where the number of different integers in that array
# is exactly k.
#
# For example, [1,2,3,1,2] has 3 different integers: 1, 2, and 3.
#
# A subarray is a contiguous part of an array.
#
# Example 1:
#
# Input: nums = [1,2,1,2,3], k = 2
# Output: 7
# Explanation: Subarrays formed with exactly 2 different integers: [1,2],
# [2,1], [1,2], [2,3], [1,2,1], [2,1,2], [1,2,1,2]
#
# Example 2:
#
# Input: nums = [1,2,1,3,4], k = 3
# Output: 3
# Explanation: Subarrays formed with exactly 3 different integers: [1,2,1,3],
# [2,1,3], [1,3,4].
#
# Constraints:
#
# 1 <= nums.length <= 2 * 10^4
#
# 1 <= nums[i], k <= nums.length
#

# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def subarraysWithKDistinct(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Exactly k distinct = (at most k) - (at most k-1). Count subarrays with
        at most t distinct via sliding window: expand right, shrink left while
        distinct > t; every right endpoint contributes (right-left+1) valid
        windows ending there.

        Algorithm (atMost sliding):
        - atMost(t): two pointers + freq map; ans += r-l+1 for each r.
        - Return atMost(k) - atMost(k-1).

        Complexity: O(n) time, O(n) space.
        """
        def at_most(t: int) -> int:
            if t < 0:
                return 0
            freq: dict = defaultdict(int)
            left = 0
            ans = 0
            distinct = 0
            for right, x in enumerate(nums):
                if freq[x] == 0:
                    distinct += 1
                freq[x] += 1
                while distinct > t:
                    y = nums[left]
                    freq[y] -= 1
                    if freq[y] == 0:
                        distinct -= 1
                    left += 1
                ans += right - left + 1
            return ans

        return at_most(k) - at_most(k - 1)
# @lc code=end
