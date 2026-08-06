#
# @lc app=leetcode id=1261 lang=python3
#
# [1261] Find Elements in a Contaminated Binary Tree
#
# https://leetcode.com/problems/find-elements-in-a-contaminated-binary-tree/description/
#
# algorithms
# Medium (84.15%)
# Likes:    1436
# Dislikes: 127
# Total Accepted:    207K
# Total Submissions: 246K
# Testcase Example:  "[\"FindElements\",\"find\",\"find\"]"
#
# Given a binary tree with the following rules:
#
# root.val == 0
#
# For any treeNode:
#
# If treeNode.val has a value x and treeNode.left != null, then
# treeNode.left.val == 2 * x + 1
#
# If treeNode.val has a value x and treeNode.right != null, then
# treeNode.right.val == 2 * x + 2
#
# Now the binary tree is contaminated, which means all treeNode.val have been
# changed to -1.
#
# Implement the FindElements class:
#
# FindElements(TreeNode* root) Initializes the object with a contaminated
# binary tree and recovers it.
#
# bool find(int target) Returns true if the target value exists in the
# recovered binary tree.
#
# Example 1:
#
# Input
# ["FindElements","find","find"]
# [[[-1,null,-1]],[1],[2]]
# Output
# [null,false,true]
# Explanation
# FindElements findElements = new FindElements([-1,null,-1]);
# findElements.find(1); // return False
# findElements.find(2); // return True
#
# Example 2:
#
# Input
# ["FindElements","find","find","find"]
# [[[-1,-1,-1,-1,-1]],[1],[3],[5]]
# Output
# [null,true,true,false]
# Explanation
# FindElements findElements = new FindElements([-1,-1,-1,-1,-1]);
# findElements.find(1); // return True
# findElements.find(3); // return True
# findElements.find(5); // return False
#
# Example 3:
#
# Input
# ["FindElements","find","find","find","find"]
# [[[-1,null,-1,-1,null,-1]],[2],[3],[4],[5]]
# Output
# [null,true,false,false,true]
# Explanation
# FindElements findElements = new FindElements([-1,null,-1,-1,null,-1]);
# findElements.find(2); // return True
# findElements.find(3); // return False
# findElements.find(4); // return False
# findElements.find(5); // return True
#
# Constraints:
#
# TreeNode.val == -1
#
# The height of the binary tree is less than or equal to 20
#
# The total number of nodes is between [1, 10^4]
#
# Total calls of find() is between [1, 10^4]
#
# 0 <= target <= 10^6
#

# @lc code=start

from typing import Optional

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right

try:
    TreeNode  # type: ignore[name-defined]
except NameError:

    class TreeNode:  # type: ignore[no-redef]
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right


class FindElements:
    def __init__(self, root: Optional[TreeNode]):
        """
        Interview explanation:
        Contaminated tree: recover values where root=0, left=2*x+1,
        right=2*x+2. DFS/BFS assign values and store in a hash set for O(1)
        find queries.

        Algorithm:
        - seen=set(); DFS(node, val): node.val=val; add to seen; recurse kids.
        - Start DFS(root, 0) if root.

        Complexity: O(n) init time/space.
        """
        self.seen = set()

        def dfs(node: Optional[TreeNode], val: int) -> None:
            if not node:
                return
            node.val = val
            self.seen.add(val)
            dfs(node.left, 2 * val + 1)
            dfs(node.right, 2 * val + 2)

        dfs(root, 0)

    def find(self, target: int) -> bool:
        """
        Interview explanation:
        Return whether target was recovered in the tree (membership in set).

        Algorithm:
        - return target in self.seen

        Complexity: O(1) average time.
        """
        return target in self.seen
# @lc code=end
