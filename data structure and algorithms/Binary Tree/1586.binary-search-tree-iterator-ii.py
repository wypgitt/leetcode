#
# @lc app=leetcode id=1586 lang=python3
#
# [1586] Binary Search Tree Iterator II
#
# https://leetcode.com/problems/binary-search-tree-iterator-ii/description/
#
# algorithms
# Medium (63.23%)
# Likes:    273
# Dislikes: 53
# Total Accepted:    17.5K
# Total Submissions: 27.7K
# Testcase Example:  "[\"BSTIterator\",\"next\",\"next\",\"prev\",\"next\",\"hasNext\",\"next\",\"next\",\"next\",\"hasNext\",\"hasPrev\",\"prev\",\"prev\"]\n[[[7,3,15,null,null,9,20]],[null],[null],[null],[null],[null],[null],[null],[null],[null],[null],[null],[null]]"
#
#
# Implement the BSTIterator class that represents an iterator over the
# in-order traversal of a binary search tree (BST):
#
# BSTIterator(TreeNode root) Initializes an object of the BSTIterator
# class. The root of the BST is given as part of the constructor. The
# pointer should be initialized to a non-existent number smaller than any
# element in the BST.
#
# boolean hasNext() Returns true if there exists a number in the traversal
# to the right of the pointer, otherwise returns false.
#
# int next() Moves the pointer to the right, then returns the number at
# the pointer.
#
# boolean hasPrev() Returns true if there exists a number in the traversal
# to the left of the pointer, otherwise returns false.
#
# int prev() Moves the pointer to the left, then returns the number at the
# pointer.
#
# Notice that by initializing the pointer to a non-existent smallest
# number, the first call to next() will return the smallest element in the
# BST.
#
# You may assume that next() and prev() calls will always be valid. That
# is, there will be at least a next/previous number in the in-order
# traversal when next()/prev() is called.
#
# Example 1:
#
# Input
# ["BSTIterator", "next", "next", "prev", "next", "hasNext", "next",
# "next", "next", "hasNext", "hasPrev", "prev", "prev"]
# [[[7, 3, 15, null, null, 9, 20]], [null], [null], [null], [null],
# [null], [null], [null], [null], [null], [null], [null], [null]]
# Output
# [null, 3, 7, 3, 7, true, 9, 15, 20, false, true, 15, 9]
#
# Explanation
# // The underlined element is where the pointer currently is.
# BSTIterator bSTIterator = new BSTIterator([7, 3, 15, null, null, 9,
# 20]); // state is   [3, 7, 9, 15, 20]
# bSTIterator.next(); // state becomes [3, 7, 9, 15, 20], return 3
# bSTIterator.next(); // state becomes [3, 7, 9, 15, 20], return 7
# bSTIterator.prev(); // state becomes [3, 7, 9, 15, 20], return 3
# bSTIterator.next(); // state becomes [3, 7, 9, 15, 20], return 7
# bSTIterator.hasNext(); // return true
# bSTIterator.next(); // state becomes [3, 7, 9, 15, 20], return 9
# bSTIterator.next(); // state becomes [3, 7, 9, 15, 20], return 15
# bSTIterator.next(); // state becomes [3, 7, 9, 15, 20], return 20
# bSTIterator.hasNext(); // return false
# bSTIterator.hasPrev(); // return true
# bSTIterator.prev(); // state becomes [3, 7, 9, 15, 20], return 15
# bSTIterator.prev(); // state becomes [3, 7, 9, 15, 20], return 9
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^5].
#
# 0 <= Node.val <= 10^6
#
# At most 10^5 calls will be made to hasNext, next, hasPrev, and prev.
#
# Follow up: Could you solve the problem without precalculating the values
# of the tree?
#
# @lc code=start
from typing import Optional, List

# Definition for a binary tree node.
try:
    TreeNode  # type: ignore[name-defined]
except NameError:

    class TreeNode:  # type: ignore[no-redef]
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right


class BSTIterator:
    def __init__(self, root: Optional["TreeNode"]):
        """
        Interview explanation:
        Premium BST Iterator II: next/hasNext plus prev/hasPrev. Flatten
        inorder to a list and keep a pointer (simplest correct design).

        Algorithm:
        - Inorder DFS into self.arr; pointer self.i = -1 (before first).

        Complexity: O(n) init time/space.
        """
        self.arr: List[int] = []
        self.i = -1

        def inorder(node: Optional["TreeNode"]) -> None:
            if not node:
                return
            inorder(node.left)
            self.arr.append(node.val)
            inorder(node.right)

        inorder(root)

    def hasNext(self) -> bool:
        """
        Interview explanation:
        True if pointer can move right within flattened inorder.

        Algorithm:
        - return i+1 < len(arr)

        Complexity: O(1).
        """
        return self.i + 1 < len(self.arr)

    def next(self) -> int:
        """
        Interview explanation:
        Move to next inorder value and return it.

        Algorithm:
        - i += 1; return arr[i]

        Complexity: O(1).
        """
        self.i += 1
        return self.arr[self.i]

    def hasPrev(self) -> bool:
        """
        Interview explanation:
        True if pointer can move left (not at first element).

        Algorithm:
        - return i > 0

        Complexity: O(1).
        """
        return self.i > 0

    def prev(self) -> int:
        """
        Interview explanation:
        Move to previous inorder value and return it.

        Algorithm:
        - i -= 1; return arr[i]

        Complexity: O(1).
        """
        self.i -= 1
        return self.arr[self.i]


# Your BSTIterator object will be instantiated and called as such:
# obj = BSTIterator(root)
# param_1 = obj.hasNext()
# param_2 = obj.next()
# param_3 = obj.hasPrev()
# param_4 = obj.prev()
# @lc code=end

