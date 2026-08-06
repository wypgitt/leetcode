#
# @lc app=leetcode id=331 lang=python3
#
# [331] Verify Preorder Serialization of a Binary Tree
#
# https://leetcode.com/problems/verify-preorder-serialization-of-a-binary-tree/description/
#
# algorithms
# Medium (47.66%)
# Likes:    2469
# Dislikes: 133
# Total Accepted:    173K
# Total Submissions: 363K
# Testcase Example:  "\"9,3,4,#,#,1,#,#,2,#,6,#,#\""
#
# One way to serialize a binary tree is to use preorder traversal. When we
# encounter a non-null node, we record the node's value. If it is a null node,
# we record using a sentinel value such as '#'.
#
# For example, the above binary tree can be serialized to the string
# "9,3,4,#,#,1,#,#,2,#,6,#,#", where '#' represents a null node.
#
# Given a string of comma-separated values preorder, return true if it is a
# correct preorder traversal serialization of a binary tree.
#
# It is guaranteed that each comma-separated value in the string must be either
# an integer or a character '#' representing null pointer.
#
# You may assume that the input format is always valid.
#
# For example, it could never contain two consecutive commas, such as "1,,3".
#
# Note: You are not allowed to reconstruct the tree.
#
# Example 1:
#
# Input: preorder = "9,3,4,#,#,1,#,#,2,#,6,#,#"
# Output: true
#
# Example 2:
#
# Input: preorder = "1,#"
# Output: false
#
# Example 3:
#
# Input: preorder = "9,#,#,1"
# Output: false
#
# Constraints:
#
# 1 <= preorder.length <= 10^4
#
# preorder consist of integers in the range [0, 100] and '#' separated by
# commas ','.
#

# @lc code=start
class Solution:
    def isValidSerialization(self, preorder: str) -> bool:
        """
        Interview explanation:
        Slot counting: a binary tree serialization needs one slot for the root.
        Each non-null node consumes one slot and creates two; null consumes one.
        Valid iff slots never go negative and end at exactly 0.

        Algorithm:
        - slots = 1.
        - For each node: slots -= 1; if slots < 0 fail; if not '#', slots += 2.
        - Return slots == 0.

        Complexity: O(n) time, O(1) space (excluding split).
        """
        slots = 1
        for node in preorder.split(","):
            slots -= 1
            if slots < 0:
                return False
            if node != "#":
                slots += 2
        return slots == 0

    def isValidSerialization_stack(self, preorder: str) -> bool:
        """
        Interview explanation:
        Alternate: stack simulation — push nodes; when top two are '#' and
        below is a value, collapse to a single '#' (finished subtree).

        Algorithm:
        - Process tokens; after each, while stack ends with val,#,# collapse.
        - Valid if final stack is exactly ['#'].

        Complexity: O(n) time and space.
        """
        stack: list[str] = []
        for node in preorder.split(","):
            stack.append(node)
            while (
                len(stack) >= 3
                and stack[-1] == "#"
                and stack[-2] == "#"
                and stack[-3] != "#"
            ):
                stack.pop()
                stack.pop()
                stack.pop()
                stack.append("#")
        return stack == ["#"]
# @lc code=end
