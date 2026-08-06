#
# @lc app=leetcode id=637 lang=python3
#
# [637] Average of Levels in Binary Tree
#
# https://leetcode.com/problems/average-of-levels-in-binary-tree/description/
#
# algorithms
# Easy (75.11%)
# Likes:    5625
# Dislikes: 352
# Total Accepted:    774K
# Total Submissions: 1.0M
# Testcase Example:  "[3,9,20,null,null,15,7]"
#
# Given the root of a binary tree, return the average value of the nodes on
# each level in the form of an array. Answers within 10^-5 of the actual answer
# will be accepted.
#
# Example 1:
#
# Input: root = [3,9,20,null,null,15,7]
# Output: [3.00000,14.50000,11.00000]
# Explanation: The average value of nodes on level 0 is 3, on level 1 is 14.5,
# and on level 2 is 11.
# Hence return [3, 14.5, 11].
#
# Example 2:
#
# Input: root = [3,9,20,15,7]
# Output: [3.00000,14.50000,11.00000]
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^4].
#
# -2^31 <= Node.val <= 2^31 - 1
#

# @lc code=start

from collections import defaultdict, deque
from typing import List, Optional

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right


class Solution:
    def averageOfLevels(self, root: Optional[TreeNode]) -> List[float]:
        """
        Interview explanation:
        Level-order BFS: for each level sum values / count.

        Algorithm:
        - Queue root; while queue: process level size, accumulate sum, enqueue children.
        - Append sum/count.

        Complexity: O(N) time, O(W) space.
        """
        if not root:
            return []
        ans = []
        q = deque([root])
        while q:
            size = len(q)
            total = 0
            for _ in range(size):
                node = q.popleft()
                total += node.val
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
            ans.append(total / size)
        return ans

    def averageOfLevels_dfs(self, root: Optional[TreeNode]) -> List[float]:
        """
        Interview explanation:
        Alternate classic: DFS tracking (sum, count) per depth, then averages.

        Algorithm:
        - DFS(node, depth): sums[depth]+=val; cnt[depth]+=1; recurse.
        - Return [sums[i]/cnt[i] for each depth].

        Complexity: O(N) time, O(H) space.
        """
        sums = defaultdict(float)
        cnt = defaultdict(int)

        def dfs(node, d):
            if not node:
                return
            sums[d] += node.val
            cnt[d] += 1
            dfs(node.left, d + 1)
            dfs(node.right, d + 1)

        dfs(root, 0)
        return [sums[i] / cnt[i] for i in range(len(sums))]
# @lc code=end
