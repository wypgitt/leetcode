#
# @lc app=leetcode id=862 lang=python3
#
# [862] Shortest Subarray with Sum at Least K
#
# https://leetcode.com/problems/shortest-subarray-with-sum-at-least-k/description/
#
# algorithms
# Hard (32.96%)
# Likes:    5257
# Dislikes: 146
# Total Accepted:    220K
# Total Submissions: 667K
# Testcase Example:  "[1]"
#
# Given an integer array nums and an integer k, return the length of the
# shortest non-empty subarray of nums with a sum of at least k. If there is no
# such subarray, return -1.
#
# A subarray is a contiguous part of an array.
#
# Example 1:
#
# Input: nums = [1], k = 1
# Output: 1
#
# Example 2:
#
# Input: nums = [1,2], k = 4
# Output: -1
#
# Example 3:
#
# Input: nums = [2,-1,2], k = 3
# Output: 3
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^5 <= nums[i] <= 10^5
#
# 1 <= k <= 10^9
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def shortestSubarray(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Negatives break plain sliding window. Use prefix sums + monotonic
        increasing deque of indices: for each right end, pop left while
        prefix[r]-prefix[dq[0]] >= k (shortest), and keep deque increasing.

        Algorithm (deque):
        - pref[0]=0, pref[i+1]=sum(nums[:i+1]).
        - dq stores indices of pref increasing.
        - For r in 0..n: while dq and pref[r]-pref[dq[0]]>=k: update ans,
          popleft. While dq and pref[r]<=pref[dq[-1]]: pop. Append r.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        pref = [0] * (n + 1)
        for i, x in enumerate(nums):
            pref[i + 1] = pref[i] + x
        ans = n + 1
        dq: deque[int] = deque()
        for r in range(n + 1):
            while dq and pref[r] - pref[dq[0]] >= k:
                ans = min(ans, r - dq.popleft())
            while dq and pref[r] <= pref[dq[-1]]:
                dq.pop()
            dq.append(r)
        return ans if ans <= n else -1
# @lc code=end

