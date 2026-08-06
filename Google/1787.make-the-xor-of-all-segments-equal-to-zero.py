#
# @lc app=leetcode id=1787 lang=python3
#
# [1787] Make the XOR of All Segments Equal to Zero
#
# https://leetcode.com/problems/make-the-xor-of-all-segments-equal-to-zero/description/
#
# algorithms
# Hard (40.86%)
# Likes:    429
# Dislikes: 27
# Total Accepted:    7.4K
# Total Submissions: 18.0K
# Testcase Example:  "[1,2,0,3,0]"
#
# You are given an array nums and an integer k. The XOR of a segment [left,
# right] where left <= right is the XOR of all the elements with indices
# between left and right, inclusive: nums[left] XOR nums[left+1] XOR ... XOR
# nums[right].
#
# Return the minimum number of elements to change in the array such that the
# XOR of all segments of size k is equal to zero.
#
# Example 1:
#
# Input: nums = [1,2,0,3,0], k = 1
# Output: 3
# Explanation: Modify the array from [1,2,0,3,0] to from [0,0,0,0,0].
#
# Example 2:
#
# Input: nums = [3,4,5,2,1,7,3,4,7], k = 3
# Output: 3
# Explanation: Modify the array from [3,4,5,2,1,7,3,4,7] to
# [3,4,7,3,4,7,3,4,7].
#
# Example 3:
#
# Input: nums = [1,2,4,1,2,5,1,2,6], k = 3
# Output: 3
# Explanation: Modify the array from [1,2,4,1,2,5,1,2,6] to
# [1,2,3,1,2,3,1,2,3].
#
# Constraints:
#
# 1 <= k <= nums.length <= 2000
#
# 0 <= nums[i] < 2^10
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def minChanges(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Make every length-k XOR segment equal 0 ⇒ the array is periodic XOR
        with period k and XOR of one period is 0. For each residue class i
        (positions ≡ i mod k), choose a value; minimize total changes.
        DP over residue: dp[j][x] = min changes for first j classes with XOR x.

        Algorithm:
        - For each of k groups: count frequencies; total = group size.
        - dp_new[x^v] = min(dp[x] + total - freq[v]) over choices v; also
          allow changing whole group to anything: min(dp)+total.

        Complexity: O(k * 2^10 * 2^10) worst; with trick O(k * (n/k + 2^{10})).
        """
        n = len(nums)
        MAX = 1 << 10
        INF = 10**9
        # dp[xor] = min changes to achieve this XOR over processed groups
        dp = [INF] * MAX
        dp[0] = 0
        for i in range(k):
            cnt = Counter(nums[j] for j in range(i, n, k))
            total = sum(cnt.values())
            ndp = [min(dp) + total] * MAX  # change all to a fresh value
            # For each previous xor and each value appearing, try keep that value
            # Optimize: for each prev xor state, best is min over v of dp[xor] + total - freq[v]
            # ≡ for each v: for each xor: ndp[xor^v] = min(..., dp[xor] + total - freq[v])
            for x in range(MAX):
                if dp[x] >= INF:
                    continue
                for v, c in cnt.items():
                    ndp[x ^ v] = min(ndp[x ^ v], dp[x] + total - c)
            dp = ndp
        return dp[0]
# @lc code=end
