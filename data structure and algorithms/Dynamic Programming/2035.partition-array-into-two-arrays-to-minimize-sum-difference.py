#
# @lc app=leetcode id=2035 lang=python3
#
# [2035] Partition Array Into Two Arrays to Minimize Sum Difference
#
# https://leetcode.com/problems/partition-array-into-two-arrays-to-minimize-sum-difference/description/
#
# algorithms
# Hard (24.23%)
# Likes:    3886
# Dislikes: 263
# Total Accepted:    66.8K
# Total Submissions: 275.8K
# Testcase Example:  "[3,9,7,3]"
#
# You are given an integer array nums of 2 * n integers. You need to partition
# nums into two arrays of length n to minimize the absolute difference of the
# sums of the arrays. To partition nums, put each element of nums into one of
# the two arrays.
#
# Return the minimum possible absolute difference.
#
#
#
# Example 1:
#
# Input: nums = [3,9,7,3]
# Output: 2
# Explanation: One optimal partition is: [3,9] and [7,3].
# The absolute difference between the sums of the arrays is abs((3 + 9) - (7 +
# 3)) = 2.
#
# Example 2:
#
# Input: nums = [-36,36]
# Output: 72
# Explanation: One optimal partition is: [-36] and [36].
# The absolute difference between the sums of the arrays is abs((-36) - (36)) =
# 72.
#
# Example 3:
#
# Input: nums = [2,-1,0,4,-2,-9]
# Output: 0
# Explanation: One optimal partition is: [2,4,-9] and [-1,0,-2].
# The absolute difference between the sums of the arrays is abs((2 + 4 + -9) -
# (-1 + 0 + -2)) = 0.
#
#
#
# Constraints:
#
#
# 1 <= n <= 15
#
#
# nums.length == 2 * n
#
#
# -10^7 <= nums[i] <= 10^7
#

# @lc code=start
from typing import List
class Solution:
    def minimumDifference(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Partition 2n elements into two arrays of size n minimizing |sum1-sum2|
        = |total - 2*sum1|. Meet-in-the-middle over half the array.

        Algorithm:
        - Split into left/right halves of n. For each k=0..n, store all subset
          sums of size k on each half. For left sum of size k, binary-search
          right sum of size n-k closest to total/2 - left.

        Complexity: O(2^n * n) time/space with N=2n, n<=15.
        """
        import bisect
        N = len(nums)
        n = N // 2
        total = sum(nums)
        left, right = nums[:n], nums[n:]

        def subset_sums(arr):
            m = len(arr)
            res = [[] for _ in range(m + 1)]
            for mask in range(1 << m):
                s = cnt = 0
                for i in range(m):
                    if mask & (1 << i):
                        s += arr[i]
                        cnt += 1
                res[cnt].append(s)
            for k in range(m + 1):
                res[k].sort()
            return res

        L = subset_sums(left)
        R = subset_sums(right)
        ans = abs(total - 2 * L[n][0]) if L[n] else abs(total)
        target = total / 2
        for k in range(n + 1):
            for s in L[k]:
                need = target - s
                arr = R[n - k]
                if not arr:
                    continue
                j = bisect.bisect_left(arr, need)
                for t in (j - 1, j):
                    if 0 <= t < len(arr):
                        ans = min(ans, abs(total - 2 * (s + arr[t])))
        return ans
# @lc code=end
