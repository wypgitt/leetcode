#
# @lc app=leetcode id=2672 lang=python3
#
# [2672] Number of Adjacent Elements With the Same Color
#
# https://leetcode.com/problems/number-of-adjacent-elements-with-the-same-color/description/
#
# algorithms
# Medium (59.79%)
# Likes:    402
# Dislikes: 120
# Total Accepted:    35.6K
# Total Submissions: 59.5K
# Testcase Example:  "4\n[[0,2],[1,2],[3,1],[1,1],[2,1]]"
#
# You are given an integer n representing an array colors of length n where all
# elements are set to 0's meaning uncolored. You are also given a 2D integer
# array queries where queries[i] = [index_i, color_i]. For the i^th query:
#
#
# Set colors[index_i] to color_i.
#
#
# Count the number of adjacent pairs in colors which have the same color
# (regardless of color_i).
#
# Return an array answer of the same length as queries where answer[i] is the
# answer to the i^th query.
#
#
#
# Example 1:
#
# Input: n = 4, queries = [[0,2],[1,2],[3,1],[1,1],[2,1]]
#
# Output: [0,1,1,0,2]
#
# Explanation:
#
#
# Initially array colors = [0,0,0,0], where 0 denotes uncolored elements of the
# array.
#
#
# After the 1^st query colors = [2,0,0,0]. The count of adjacent pairs with the
# same color is 0.
#
#
# After the 2^nd query colors = [2,2,0,0]. The count of adjacent pairs with the
# same color is 1.
#
#
# After the 3^rd query colors = [2,2,0,1]. The count of adjacent pairs with the
# same color is 1.
#
#
# After the 4^th query colors = [2,1,0,1]. The count of adjacent pairs with the
# same color is 0.
#
#
# After the 5^th query colors = [2,1,1,1]. The count of adjacent pairs with the
# same color is 2.
#
# Example 2:
#
# Input: n = 1, queries = [[0,100000]]
#
# Output: [0]
#
# Explanation:
#
# After the 1^st query colors = [100000]. The count of adjacent pairs with the
# same color is 0.
#
#
#
# Constraints:
#
#
# 1 <= n <= 10^5
#
#
# 1 <= queries.length <= 10^5
#
#
# queries[i].length == 2
#
#
# 0 <= index_i <= n - 1
#
#
# 1 <=  color_i <= 10^5
#

# @lc code=start

from typing import List


class Solution:
    def colorTheArray(self, n: int, queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Array of n zeros (uncolored). queries[i]=[index,color] paints that index. After each query,
        return count of adjacent equal nonzero color pairs.

        Algorithm:
        - Maintain running adjacent-same count; before/after paint, adjust pairs with neighbors.

        Complexity: O(q) time, O(n) space.
        """
        colors = [0] * n
        ans = []
        same = 0
        for idx, color in queries:
            if colors[idx] != 0:
                if idx > 0 and colors[idx] == colors[idx - 1]:
                    same -= 1
                if idx + 1 < n and colors[idx] == colors[idx + 1]:
                    same -= 1
            colors[idx] = color
            if idx > 0 and colors[idx] == colors[idx - 1]:
                same += 1
            if idx + 1 < n and colors[idx] == colors[idx + 1]:
                same += 1
            ans.append(same)
        return ans
# @lc code=end
