#
# @lc app=leetcode id=666 lang=python3
#
# [666] Path Sum IV
#
# https://leetcode.com/problems/path-sum-iv/description/
#
# algorithms
# Medium (62.88%)
# Likes:    428
# Dislikes: 524
# Total Accepted:    41.9K
# Total Submissions: 66.6K
# Testcase Example:  "[113,215,221]"
#
#
# If the depth of a tree is smaller than 5, then this tree can be
# represented by an array of three-digit integers. You are given an
# ascending array nums consisting of three-digit integers representing a
# binary tree with a depth smaller than 5, where for each integer:
#
# The hundreds digit represents the depth d of this node, where 1 <= d <=
# 4.
#
# The tens digit represents the position p of this node within its level,
# where 1 <= p <= 8, corresponding to its position in a full binary tree.
#
# The units digit represents the value v of this node, where 0 <= v <= 9.
#
# Return the sum of all paths from the root towards the leaves.
#
# It is guaranteed that the given array represents a valid connected
# binary tree.
#
# Example 1:
#
# Input: nums = [113,215,221]
#
# Output: 12
#
# Explanation:
#
# The tree that the list represents is shown.
#
# The path sum is (3 + 5) + (3 + 1) = 12.
#
# Example 2:
#
# Input: nums = [113,221]
#
# Output: 4
#
# Explanation:
#
# The tree that the list represents is shown.
#
# The path sum is (3 + 1) = 4.
#
# Constraints:
#
# 1 <= nums.length <= 15
#
# 110 <= nums[i] <= 489
#
# nums represents a valid binary tree with depth less than 5.
#
# nums is sorted in ascending order.
#
# @lc code=start
from typing import List


class Solution:
    def pathSum(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Premium: each int encodes depth D, position P, value V as 100*D+10*P+V
        in a complete-binary-tree layout. Sum all root-to-leaf path sums; a node
        is a leaf if both children are missing from the encoding.

        Algorithm:
        - Map (depth, pos) -> value.
        - DFS from (1,1) accumulating path; if no children, add path to answer;
          else recurse to (d+1, 2*p-1) and (d+1, 2*p).

        Complexity: O(n) time and space.
        """
        tree = {}
        for x in nums:
            d, p, v = x // 100, (x // 10) % 10, x % 10
            tree[(d, p)] = v
        ans = 0

        def dfs(d: int, p: int, path: int) -> None:
            nonlocal ans
            if (d, p) not in tree:
                return
            path += tree[(d, p)]
            left = (d + 1, 2 * p - 1)
            right = (d + 1, 2 * p)
            if left not in tree and right not in tree:
                ans += path
                return
            dfs(left[0], left[1], path)
            dfs(right[0], right[1], path)

        dfs(1, 1, 0)
        return ans
# @lc code=end
