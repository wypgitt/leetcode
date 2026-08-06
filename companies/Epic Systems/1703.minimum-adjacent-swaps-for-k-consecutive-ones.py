#
# @lc app=leetcode id=1703 lang=python3
#
# [1703] Minimum Adjacent Swaps for K Consecutive Ones
#
# https://leetcode.com/problems/minimum-adjacent-swaps-for-k-consecutive-ones/description/
#
# algorithms
# Hard (42.47%)
# Likes:    755
# Dislikes: 29
# Total Accepted:    15.0K
# Total Submissions: 35.3K
# Testcase Example:  "[1,0,0,1,0,1]"
#
# You are given an integer array, nums, and an integer k. nums comprises of
# only 0's and 1's. In one move, you can choose two adjacent indices and swap
# their values.
#
# Return the minimum number of moves required so that nums has k consecutive
# 1's.
#
# Example 1:
#
# Input: nums = [1,0,0,1,0,1], k = 2
# Output: 1
# Explanation: In 1 move, nums could be [1,0,0,0,1,1] and have 2 consecutive
# 1's.
#
# Example 2:
#
# Input: nums = [1,0,0,0,0,0,1,1], k = 3
# Output: 5
# Explanation: In 5 moves, the leftmost 1 can be shifted right until nums =
# [0,0,0,0,0,1,1,1].
#
# Example 3:
#
# Input: nums = [1,1,0,1], k = 2
# Output: 0
# Explanation: nums already has 2 consecutive 1's.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# nums[i] is 0 or 1.
#
# 1 <= k <= sum(nums)
#

# @lc code=start
from typing import List


class Solution:
    def minMoves(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Positions of ones must become k consecutive. Sliding windows of k ones;
        gather cost to median on transformed positions pos[i]-i (already accounts
        for consecutive packing), which equals minimum adjacent swaps.

        Algorithm:
        - pos = indices of ones; a[i] = pos[i]-i
        - Prefix sums of a; for each window of size k, cost = sum|a[j]-a[median]|
        - Return minimum window cost.

        Complexity: O(m) time, O(m) space (m = number of ones).
        """
        pos = [i for i, x in enumerate(nums) if x == 1]
        m = len(pos)
        if k <= 1:
            return 0
        a = [pos[i] - i for i in range(m)]
        pref = [0]
        for v in a:
            pref.append(pref[-1] + v)
        ans = float("inf")
        for i in range(m - k + 1):
            mid = i + k // 2
            left = a[mid] * (mid - i) - (pref[mid] - pref[i])
            right = (pref[i + k] - pref[mid + 1]) - a[mid] * (i + k - mid - 1)
            ans = min(ans, left + right)
        return int(ans)

    def minMoves_prefixMedian(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate view: gather raw positions to median, then subtract the fixed
        triangular offset needed to pack into consecutive indices around median.

        Algorithm:
        - pos ones; prefix of pos; for window, median gather minus sum of offsets.

        Complexity: O(m) time, O(m) space.
        """
        pos = [i for i, x in enumerate(nums) if x == 1]
        m = len(pos)
        if k <= 1:
            return 0
        pref = [0]
        for p in pos:
            pref.append(pref[-1] + p)
        ans = float("inf")
        for i in range(m - k + 1):
            mid = i + k // 2
            # sum |pos[j]-pos[mid]| for j in [i,i+k)
            left = pos[mid] * (mid - i) - (pref[mid] - pref[i])
            right = (pref[i + k] - pref[mid + 1]) - pos[mid] * (i + k - mid - 1)
            # subtract ideal consecutive radii
            # left radius: (mid-i)*(mid-i+1)//2 ; right: (i+k-1-mid)*(i+k-mid)//2
            radius = (mid - i) * (mid - i + 1) // 2 + (i + k - 1 - mid) * (i + k - mid) // 2
            ans = min(ans, left + right - radius)
        return int(ans)
# @lc code=end
