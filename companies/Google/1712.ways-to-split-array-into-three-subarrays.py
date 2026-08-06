#
# @lc app=leetcode id=1712 lang=python3
#
# [1712] Ways to Split Array Into Three Subarrays
#
# https://leetcode.com/problems/ways-to-split-array-into-three-subarrays/description/
#
# algorithms
# Medium (34.5%)
# Likes:    1517
# Dislikes: 114
# Total Accepted:    42.8K
# Total Submissions: 124K
# Testcase Example:  "[1,1,1]"
#
# A split of an integer array is good if:
#
# The array is split into three non-empty contiguous subarrays - named left,
# mid, right respectively from left to right.
#
# The sum of the elements in left is less than or equal to the sum of the
# elements in mid, and the sum of the elements in mid is less than or equal to
# the sum of the elements in right.
#
# Given nums, an array of non-negative integers, return the number of good ways
# to split nums. As the number may be too large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: nums = [1,1,1]
# Output: 1
# Explanation: The only good way to split nums is [1] [1] [1].
#
# Example 2:
#
# Input: nums = [1,2,2,2,5,0]
# Output: 3
# Explanation: There are three good ways of splitting nums:
# [1] [2] [2,2,5,0]
# [1] [2,2] [2,5,0]
# [1,2] [2,2] [5,0]
#
# Example 3:
#
# Input: nums = [3,2,1]
# Output: 0
# Explanation: There is no good way to split nums.
#
# Constraints:
#
# 3 <= nums.length <= 10^5
#
# 0 <= nums[i] <= 10^4
#

# @lc code=start
from typing import List
import bisect


class Solution:
    def waysToSplit(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Split into 3 non-empty contiguous parts with left <= mid <= right sums.
        Prefix sums + for each left end i, binary search valid mid ends.

        Algorithm:
        - pref[i] = sum nums[:i]
        - For i in 1..n-2: left = pref[i]; find smallest j > i with pref[j]-left >= left
          and largest j < n with pref[n]-pref[j] >= pref[j]-left; add count.

        Complexity: O(n log n) time, O(n) space.
        """
        MOD = 10**9 + 7
        n = len(nums)
        pref = [0]
        for x in nums:
            pref.append(pref[-1] + x)
        total = pref[n]
        ans = 0
        for i in range(1, n - 1):
            left = pref[i]
            # j from i+1 .. n-1; mid = pref[j]-left; right = total-pref[j]
            # mid >= left => pref[j] >= 2*left
            # right >= mid => total-pref[j] >= pref[j]-left => pref[j] <= (total+left)//2
            lo = bisect.bisect_left(pref, 2 * left, i + 1, n)
            hi = bisect.bisect_right(pref, (total + left) // 2, i + 1, n) - 1
            if lo <= hi and hi <= n - 1:
                ans = (ans + hi - lo + 1) % MOD
        return ans

    def waysToSplit_twopointer(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate O(n): two advancing pointers for left/right bounds of mid end
        as left end grows (prefix monotone).

        Algorithm:
        - Maintain j,k pointers for valid mid range for each i.

        Complexity: O(n) time, O(n) space.
        """
        MOD = 10**9 + 7
        n = len(nums)
        pref = [0]
        for x in nums:
            pref.append(pref[-1] + x)
        total = pref[n]
        ans = 0
        j = k = 1
        for i in range(1, n - 1):
            left = pref[i]
            j = max(j, i + 1)
            while j < n and pref[j] < 2 * left:
                j += 1
            while k < n and pref[k] <= (total + left) // 2:
                k += 1
            # valid mid ends j .. min(k-1, n-1)
            r = min(k - 1, n - 1)
            if j <= r:
                ans = (ans + r - j + 1) % MOD
        return ans
# @lc code=end
