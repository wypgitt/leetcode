#
# @lc app=leetcode id=1214 lang=python3
#
# [1214] Two Sum BSTs
#
# https://leetcode.com/problems/two-sum-bsts/description/
#
# algorithms
# Medium (68.17%)
# Likes:    580
# Dislikes: 46
# Total Accepted:    62.3K
# Total Submissions: 91.4K
# Testcase Example:  "[2,1,4]\n[1,0,3]\n5"
#
#
# Given the roots of two binary search trees, root1 and root2, return true
# if and only if there is a node in the first tree and a node in the
# second tree whose values sum up to a given integer target.
#
# Example 1:
#
# Input: root1 = [2,1,4], root2 = [1,0,3], target = 5
# Output: true
# Explanation: 2 and 3 sum up to 5.
#
# Example 2:
#
# Input: root1 = [0,-10,10], root2 = [5,1,7,0,2], target = 18
# Output: false
#
# Constraints:
#
# The number of nodes in each tree is in the range [1, 5000].
#
# -10^9 <= Node.val, target <= 10^9
#
# @lc code=start
from typing import Optional

# Definition for a binary tree node.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def twoSumBSTs(self, root1: Optional[TreeNode], root2: Optional[TreeNode], target: int) -> bool:
        """
        Interview explanation:
        Premium. Find if there exist nodes from two BSTs summing to target.
        Put all values of one tree in a hash set; search target-v in the other.

        Algorithm:
        - DFS collect set from root1; DFS root2 checking target-val in set

        Complexity: O(n+m) time/space.
        """
        vals = set()

        def collect(node: Optional[TreeNode]) -> None:
            if not node:
                return
            vals.add(node.val)
            collect(node.left)
            collect(node.right)

        collect(root1)

        def search(node: Optional[TreeNode]) -> bool:
            if not node:
                return False
            if target - node.val in vals:
                return True
            return search(node.left) or search(node.right)

        return search(root2)

    def twoSumBSTs_twopointers(self, root1: Optional[TreeNode], root2: Optional[TreeNode], target: int) -> bool:
        """
        Interview explanation:
        Alternate: inorder both trees to sorted arrays; two-pointer from ends
        (or left of one + right of other) seeking target sum.

        Algorithm:
        - Inorder to lists A,B; i=0,j=len(B)-1; move based on A[i]+B[j] vs target

        Complexity: O(n+m) time/space.
        """
        def inorder(node, out):
            if not node:
                return
            inorder(node.left, out)
            out.append(node.val)
            inorder(node.right, out)

        A, B = [], []
        inorder(root1, A)
        inorder(root2, B)
        i, j = 0, len(B) - 1
        while i < len(A) and j >= 0:
            s = A[i] + B[j]
            if s == target:
                return True
            if s < target:
                i += 1
            else:
                j -= 1
        return False
# @lc code=end
