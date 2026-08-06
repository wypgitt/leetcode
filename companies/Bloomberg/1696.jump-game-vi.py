#
# @lc app=leetcode id=1696 lang=python3
#
# [1696] Jump Game VI
#
# https://leetcode.com/problems/jump-game-vi/description/
#
# algorithms
# Medium (46.55%)
# Likes:    3599
# Dislikes: 129
# Total Accepted:    134K
# Total Submissions: 289K
# Testcase Example:  "[1,-1,-2,4,-7,3]"
#
# You are given a 0-indexed integer array nums and an integer k.
#
# You are initially standing at index 0. In one move, you can jump at most k
# steps forward without going outside the boundaries of the array. That is, you
# can jump from index i to any index in the range [i + 1, min(n - 1, i + k)]
# inclusive.
#
# You want to reach the last index of the array (index n - 1). Your score is
# the sum of all nums[j] for each index j you visited in the array.
#
# Return the maximum score you can get.
#
# Example 1:
#
# Input: nums = [1,-1,-2,4,-7,3], k = 2
# Output: 7
# Explanation: You can choose your jumps forming the subsequence [1,-1,4,3]
# (underlined above). The sum is 7.
#
# Example 2:
#
# Input: nums = [10,-5,-2,4,0,3], k = 3
# Output: 17
# Explanation: You can choose your jumps forming the subsequence [10,4,3]
# (underlined above). The sum is 17.
#
# Example 3:
#
# Input: nums = [1,-5,-20,4,-1,3,-6,-3], k = 2
# Output: 0
#
# Constraints:
#
# 1 <= nums.length, k <= 10^5
#
# -10^4 <= nums[i] <= 10^4
#

# @lc code=start
from typing import List
from collections import deque
import heapq


class Solution:
    def maxResult(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Jump game: from i jump to i+1..i+k; score sum of visited. Max score:
        dp[i]=nums[i]+max(dp[i-k..i-1]). Monotonic deque for range max.

        Algorithm (DP + monoqueue):
        - dq stores indices decreasing dp; dp[i]=nums[i]+dp[dq[0]]; push i.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        dp = [0] * n
        dp[0] = nums[0]
        dq = deque([0])
        for i in range(1, n):
            while dq and dq[0] < i - k:
                dq.popleft()
            dp[i] = nums[i] + dp[dq[0]]
            while dq and dp[dq[-1]] <= dp[i]:
                dq.pop()
            dq.append(i)
        return dp[-1]

    def maxResult_heap(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: max-heap of (dp[j], j) for j in [i-k,i); lazy discard stale.

        Algorithm:
        - heap=(-dp[0],0); for i: pop while j<i-k; dp[i]=nums[i]-heap[0][0]; push.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(nums)
        dp0 = nums[0]
        heap = [(-dp0, 0)]
        cur = dp0
        for i in range(1, n):
            while heap[0][1] < i - k:
                heapq.heappop(heap)
            cur = nums[i] - heap[0][0]
            heapq.heappush(heap, (-cur, i))
        return cur
# @lc code=end
