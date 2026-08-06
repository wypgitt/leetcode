#
# @lc app=leetcode id=96 lang=python3
#
# [96] Unique Binary Search Trees
#
# https://leetcode.com/problems/unique-binary-search-trees/description/
#
# algorithms
# Medium (63.67%)
# Likes:    11034
# Dislikes: 448
# Total Accepted:    868.3K
# Total Submissions: 1.4M
# Testcase Example:  '3'
#
# Given an integer n, return the number of structurally unique BST's (binary
# search trees) which has exactly n nodes of unique values from 1 to n.
# 
# 
# Example 1:
# 
# 
# Input: n = 3
# Output: 5
# 
# 
# Example 2:
# 
# 
# Input: n = 1
# Output: 1
# 
# 
# 
# Constraints:
# 
# 
# 1 <= n <= 19
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def numTrees(self, n: int) -> int:
        """
        Interview explanation:
        Choosing each value as the root splits the remaining values into an
        independent left subtree and right subtree. If the left side has k nodes
        and the right has n-1-k nodes, the number of trees is dp[k] *
        dp[n-1-k]. This is the Catalan recurrence.

        Edge cases and tests:
        - n=1 returns 1.
        - dp[0]=1 represents an empty subtree.
        - n=3 returns 5.

        Complexity: O(n^2) time, O(n) space.
        """
        dp = [0] * (n + 1)
        dp[0] = dp[1] = 1
        for nodes in range(2, n + 1):
            total = 0
            for left_count in range(nodes):
                total += dp[left_count] * dp[nodes - 1 - left_count]
            dp[nodes] = total
        return dp[n]
# @lc code=end


