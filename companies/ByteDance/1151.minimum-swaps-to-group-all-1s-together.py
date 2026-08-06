#
# @lc app=leetcode id=1151 lang=python3
#
# [1151] Minimum Swaps to Group All 1's Together
#
# https://leetcode.com/problems/minimum-swaps-to-group-all-1s-together/description/
#
# algorithms
# Medium (61.27%)
# Likes:    1283
# Dislikes: 18
# Total Accepted:    89.5K
# Total Submissions: 146.1K
# Testcase Example:  "[1,0,1,0,1]"
#
#
# Given a binary array data, return the minimum number of swaps required
# to group all 1’s present in the array together in any place in the
# array.
#
# Example 1:
#
# Input: data = [1,0,1,0,1]
# Output: 1
# Explanation: There are 3 ways to group all 1's together:
# [1,1,1,0,0] using 1 swap.
# [0,1,1,1,0] using 2 swaps.
# [0,0,1,1,1] using 1 swap.
# The minimum is 1.
#
# Example 2:
#
# Input: data = [0,0,0,1,0]
# Output: 0
# Explanation: Since there is only one 1 in the array, no swaps are
# needed.
#
# Example 3:
#
# Input: data = [1,0,1,0,1,0,0,1,1,0,1]
# Output: 3
# Explanation: One possible solution that uses 3 swaps is
# [0,0,0,0,0,1,1,1,1,1,1].
#
# Constraints:
#
# 1 <= data.length <= 10^5
#
# data[i] is either 0 or 1.
#
# @lc code=start
from typing import List


class Solution:
    def minSwaps(self, data: List[int]) -> int:
        """
        Interview explanation:
        Premium. Min swaps to group all 1s together (contiguous). Window size =
        total ones; minimize zeros inside any window of that size (= swaps).

        Algorithm (sliding window):
        - ones = sum(data); slide window of length ones; track max ones in window;
          answer = ones - max_ones_in_window.

        Complexity: O(n) time, O(1) space.
        """
        ones = sum(data)
        if ones <= 1:
            return 0
        cur = sum(data[:ones])
        best = cur
        for i in range(ones, len(data)):
            cur += data[i] - data[i - ones]
            best = max(best, cur)
        return ones - best
# @lc code=end
