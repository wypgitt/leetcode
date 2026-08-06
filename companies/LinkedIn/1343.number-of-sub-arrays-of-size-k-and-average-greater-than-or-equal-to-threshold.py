#
# @lc app=leetcode id=1343 lang=python3
#
# [1343] Number of Sub-arrays of Size K and Average Greater than or Equal to Threshold
#
# https://leetcode.com/problems/number-of-sub-arrays-of-size-k-and-average-greater-than-or-equal-to-threshold/description/
#
# algorithms
# Medium (73.71%)
# Likes:    1892
# Dislikes: 112
# Total Accepted:    219K
# Total Submissions: 297K
# Testcase Example:  "[2,2,2,2,5,5,5,8]"
#
# Given an array of integers arr and two integers k and threshold, return the
# number of sub-arrays of size k and average greater than or equal to
# threshold.
#
# Example 1:
#
# Input: arr = [2,2,2,2,5,5,5,8], k = 3, threshold = 4
# Output: 3
# Explanation: Sub-arrays [2,5,5],[5,5,5] and [5,5,8] have averages 4, 5 and 6
# respectively. All other sub-arrays of size 3 have averages less than 4 (the
# threshold).
#
# Example 2:
#
# Input: arr = [11,13,17,23,29,31,7,5,2,3], k = 3, threshold = 5
# Output: 6
# Explanation: The first 6 sub-arrays of size 3 have averages greater than 5.
# Note that averages are not integers.
#
# Constraints:
#
# 1 <= arr.length <= 10^5
#
# 1 <= arr[i] <= 10^4
#
# 1 <= k <= arr.length
#
# 0 <= threshold <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def numOfSubarrays(self, arr: List[int], k: int, threshold: int) -> int:
        """
        Interview explanation:
        Count windows of size k with average >= threshold iff sum >= k*threshold.
        Sliding window sum.

        Algorithm:
        - Need = k*threshold; maintain window sum; count.

        Complexity: O(n) time, O(1) space.
        """
        need = k * threshold
        s = sum(arr[:k])
        ans = int(s >= need)
        for i in range(k, len(arr)):
            s += arr[i] - arr[i - k]
            ans += s >= need
        return ans
# @lc code=end

