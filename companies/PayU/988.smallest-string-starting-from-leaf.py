#
# @lc app=leetcode id=988 lang=python3
#
# [988] Smallest String Starting From Leaf
#

# --- Interview notes (leaf-to-root string, DFS backtracking, lex order, complexity, pruning ideas) ---
#
# Problem
# Binary tree nodes hold **`0 … 25`** meaning **`'a' … 'z'`**. For each root-to-leaf path, form the string read **from leaf up
# to root** (first character is the leaf label, last is the root label). Return the **lexicographically smallest** such
# string among all leaves.
#
# Modeling paths
# DFS from root maintains the sequence of labels **`root → … → current`** in a list **`path`**. At a **leaf**, the required
# string is **`path` reversed** as characters — equivalently **`''.join(reversed(path))`**.
#
# Algorithm — DFS + backtracking
# • Append **`chr(ord('a') + node.val)`** when entering a node.
# • If leaf (**both children absent**), compare candidate string to **`best`** and update **`best`** if smaller.
# • Recurse left/right, then **`pop()`** to restore **`path`** for sibling subtrees (standard backtracking).
#
# Lexicographic minimum
# Python compares strings lexicographically with **`<`**. Initialize **`best`** to a sentinel strictly larger than any answer
# (e.g. **`'{'`**, the ASCII successor of **`'z'`**) or **`None`** plus branch on first leaf.
#
# Why DFS not BFS
# Every leaf must be examined; traversal order irrelevant for correctness. **DFS** matches natural recursion depth = path length.
#
# Data structures
# • **`path: list[str]`** — **O(h)** stack frames / path length **`h`**.
# • Result **`best`** — **O(h)** string storage worst-case copy when updating (acceptable).
#
# Time complexity **O(n · h)** worst-case string work across leaves — **O(n)** nodes visited; each leaf reverse/compare costs
# **O(h)** where **`h`** is height ( **`≤ n`** ). Tighter bound **O(n)** tree traversal plus total length of all generated strings
# in worst case **O(n · h)**.
#
# Space complexity **O(h)** recursion stack plus **`path`** (**`h`**); output length **O(h)**.
#
# Edge cases
# • **Single-node tree** — answer is one letter **`chr(ord('a') + root.val)`**.
# • **Balanced tree** — many leaves; each candidate compared.
#
# Improvements (optional)
# • **Early pruning:** keep **`best`** and stop expanding when the fixed suffix built so far already exceeds **`best`** under
# lex order — trickier because construction is root-down while comparison reads leaf-up; advanced optimization.
# • **Iterative DFS** with explicit stack — **O(h)** space without recursion limits.
#
# Tests (sanity)
# • Root-only **`val = 0`** → **`"a"`**.
#
# --- end notes ---

# @lc code=start
from typing import Optional


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def smallestFromLeaf(self, root: Optional[TreeNode]) -> str:
        best = "{"

        def dfs(node: Optional[TreeNode], path: list) -> None:
            nonlocal best
            if not node:
                return
            path.append(chr(ord("a") + node.val))
            if not node.left and not node.right:
                cand = "".join(reversed(path))
                if cand < best:
                    best = cand
            else:
                dfs(node.left, path)
                dfs(node.right, path)
            path.pop()

        dfs(root, [])
        return best


# @lc code=end
