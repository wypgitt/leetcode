#
# @lc app=leetcode id=1477 lang=python3
#
# [1477] Find Two Non-overlapping Sub-arrays Each With Target Sum
#
# https://leetcode.com/problems/find-two-non-overlapping-sub-arrays-each-with-target-sum/description/
#
# algorithms
# Medium (36.96%)
# Likes:    1781
# Dislikes: 95
# Total Accepted:    56.5K
# Total Submissions: 153K
# Testcase Example:  "[3,2,2,4,3]"
#
# You are given an array of integers arr and an integer target.
#
# You have to find two non-overlapping sub-arrays of arr each with a sum equal
# target. There can be multiple answers so you have to find an answer where the
# sum of the lengths of the two sub-arrays is minimum.
#
# Return the minimum sum of the lengths of the two required sub-arrays, or
# return -1 if you cannot find such two sub-arrays.
#
# Example 1:
#
# Input: arr = [3,2,2,4,3], target = 3
# Output: 2
# Explanation: Only two sub-arrays have sum = 3 ([3] and [3]). The sum of their
# lengths is 2.
#
# Example 2:
#
# Input: arr = [7,3,4,7], target = 7
# Output: 2
# Explanation: Although we have three non-overlapping sub-arrays of sum = 7
# ([7], [3,4] and [7]), but we will choose the first and third sub-arrays as
# the sum of their lengths is 2.
#
# Example 3:
#
# Input: arr = [4,3,2,6,2,3,4], target = 6
# Output: -1
# Explanation: We have only one sub-array of sum = 6.
#
# Constraints:
#
# 1 <= arr.length <= 10^5
#
# 1 <= arr[i] <= 1000
#
# 1 <= target <= 10^8
#

# @lc code=start
from typing import List


class Solution:
    def minSumOfLengths(self, arr: List[int], target: int) -> int:
        """
        Interview explanation:
        Find two non-overlapping subarrays each summing to target with minimal
        total length. Sliding window finds all target subarrays; keep best
        length to the left while scanning.

        Algorithm:
        - Window for sum==target; best[i]=min length of target subarray ending
          at or before i. Track min left length while finding windows; update ans.

        Complexity: O(n) time, O(n) space.
        """
        n = len(arr)
        INF = 10**9
        best = [INF] * n
        ans = INF
        left_best = INF
        s = 0
        lo = 0
        for hi in range(n):
            s += arr[hi]
            while s > target:
                s -= arr[lo]
                lo += 1
            if s == target:
                length = hi - lo + 1
                if lo > 0:
                    ans = min(ans, best[lo - 1] + length)
                left_best = min(left_best, length)
            best[hi] = left_best
        return -1 if ans >= INF else ans
# @lc code=end
