#
# @lc app=leetcode id=624 lang=python3
#
# [624] Maximum Distance in Arrays
#
# https://leetcode.com/problems/maximum-distance-in-arrays/description/
#
# algorithms
# Medium (45.6%)
# Likes:    1536
# Dislikes: 122
# Total Accepted:    212K
# Total Submissions: 464K
# Testcase Example:  "[[1,2,3],[4,5],[1,2,3]]"
#
# You are given m arrays, where each array is sorted in ascending order.
#
# You can pick up two integers from two different arrays (each array picks one)
# and calculate the distance. We define the distance between two integers a and
# b to be their absolute difference |a - b|.
#
# Return the maximum distance.
#
# Example 1:
#
# Input: arrays = [[1,2,3],[4,5],[1,2,3]]
# Output: 4
# Explanation: One way to reach the maximum distance 4 is to pick 1 in the
# first or third array and pick 5 in the second array.
#
# Example 2:
#
# Input: arrays = [[1],[1]]
# Output: 0
#
# Constraints:
#
# m == arrays.length
#
# 2 <= m <= 10^5
#
# 1 <= arrays[i].length <= 500
#
# -10^4 <= arrays[i][j] <= 10^4
#
# arrays[i] is sorted in ascending order.
#
# There will be at most 10^5 integers in all the arrays.
#

# @lc code=start

from typing import List


class Solution:
    def maxDistance(self, arrays: List[List[int]]) -> int:
        """
        Interview explanation:
        Each array is sorted. Max |a-b| with a,b from different arrays equals
        max of (global max - other min) style tracking one pass.

        Algorithm:
        - Track running min_so_far / max_so_far across previous arrays.
        - For each array, update ans with |arr[-1]-min| and |max-arr[0]|.
        - Then update min/max with arr[0]/arr[-1].

        Complexity: O(M) over number of arrays (only ends matter), O(1) space.
        """
        ans = 0
        cur_min, cur_max = arrays[0][0], arrays[0][-1]
        for i in range(1, len(arrays)):
            arr = arrays[i]
            ans = max(ans, abs(arr[-1] - cur_min), abs(cur_max - arr[0]))
            cur_min = min(cur_min, arr[0])
            cur_max = max(cur_max, arr[-1])
        return ans
# @lc code=end
