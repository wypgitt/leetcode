#
# @lc app=leetcode id=995 lang=python3
#
# [995] Minimum Number of K Consecutive Bit Flips
#
# https://leetcode.com/problems/minimum-number-of-k-consecutive-bit-flips/description/
#
# algorithms
# Hard (62.38%)
# Likes:    2091
# Dislikes: 91
# Total Accepted:    146K
# Total Submissions: 234K
# Testcase Example:  "[0,1,0]"
#
# You are given a binary array nums and an integer k.
#
# A k-bit flip is choosing a subarray of length k from nums and simultaneously
# changing every 0 in the subarray to 1, and every 1 in the subarray to 0.
#
# Return the minimum number of k-bit flips required so that there is no 0 in
# the array. If it is not possible, return -1.
#
# A subarray is a contiguous part of the array.
#
# Example 1:
#
# Input: nums = [0,1,0], k = 1
# Output: 2
# Explanation: Flip nums[0], then flip nums[2].
#
# Example 2:
#
# Input: nums = [1,1,0], k = 2
# Output: -1
# Explanation: No matter how we flip subarrays of size 2, we cannot make the
# array become [1,1,1].
#
# Example 3:
#
# Input: nums = [0,0,0,1,0,1,1,0], k = 3
# Output: 3
# Explanation:
# Flip nums[0],nums[1],nums[2]: nums becomes [1,1,1,1,0,1,1,0]
# Flip nums[4],nums[5],nums[6]: nums becomes [1,1,1,1,1,0,0,0]
# Flip nums[5],nums[6],nums[7]: nums becomes [1,1,1,1,1,1,1,1]
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= k <= nums.length
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def minKBitFlips(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Greedy left-to-right: whenever current bit (after prior flips) is 0,
        must flip starting here. Track flip parity with a difference queue of
        flip-start indices: an index i is flipped once for each start in
        (i-k, i]. Deque stores starts still covering i.

        Algorithm (deque difference):
        - q = deque of flip start indices; flips = 0.
        - For i, pop starts with start <= i-k. flipped = len(q) % 2.
        - If nums[i] ^ flipped == 0: need flip; if i+k > n return -1;
          append i; flips += 1.
        - Return flips.

        Complexity: O(n) time, O(n) space (deque).
        """
        n = len(nums)
        q: deque = deque()
        flips = 0
        for i in range(n):
            while q and q[0] <= i - k:
                q.popleft()
            if nums[i] ^ (len(q) % 2) == 0:
                if i + k > n:
                    return -1
                q.append(i)
                flips += 1
        return flips

    def minKBitFlips_diff_array(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate difference array: is_flipped[i] marks a flip start; running
        flip parity via prefix of the difference array.

        Algorithm:
        - diff[i] += 1 when flip at i; flip effect ends at i+k (diff[i+k] -= 1).
        - cur = running sum of diff; if nums[i]^cur==0 flip at i.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        diff = [0] * (n + 1)
        cur = 0
        flips = 0
        for i in range(n):
            cur += diff[i]
            if nums[i] ^ (cur & 1) == 0:
                if i + k > n:
                    return -1
                flips += 1
                cur += 1
                diff[i] += 1
                diff[i + k] -= 1
        return flips
# @lc code=end
