# LeetCode 156. Binary Tree Upside Down
# https://leetcode.com/problems/binary-tree-upside-down/


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def upsideDownBinaryTree(self, root: TreeNode | None) -> TreeNode | None:
        curr = root
        parent = None
        parent_right = None  # old right sibling of `parent` → becomes new left child

        while curr:
            left = curr.left
            right = curr.right

            curr.left = parent_right
            curr.right = parent

            parent_right = right
            parent = curr
            curr = left

        return parent


# Alternative: recursive (O(h) stack space)
class SolutionRecursive:
    def upsideDownBinaryTree(self, root: TreeNode | None) -> TreeNode | None:
        if not root or not root.left:
            return root

        new_root = self.upsideDownBinaryTree(root.left)

        root.left.left = root.right
        root.left.right = root
        root.left = None
        root.right = None

        return new_root
