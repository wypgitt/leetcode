#
# @lc app=leetcode id=1104 lang=python3
#
# [1104] Path In Zigzag Labelled Binary Tree
#
# https://leetcode.com/problems/path-in-zigzag-labelled-binary-tree/description/
#
# algorithms
# Medium (75.84%)
# Likes:    1552
# Dislikes: 331
# Total Accepted:    54.7K
# Total Submissions: 72.1K
# Testcase Example:  "14"
#
# In an infinite binary tree where every node has two children, the nodes are
# labelled in row order.
#
# In the odd numbered rows (ie., the first, third, fifth,...), the labelling is
# left to right, while in the even numbered rows (second, fourth, sixth,...),
# the labelling is right to left.
#
# Given the label of a node in this tree, return the labels in the path from
# the root of the tree to the node with that label.
#
# Example 1:
#
# Input: label = 14
# Output: [1,3,4,14]
#
# Example 2:
#
# Input: label = 26
# Output: [1,2,6,10,26]
#
# Constraints:
#
# 1 <= label <= 10^6
#

# @lc code=start
from typing import List


class Solution:
    def pathInZigZagTree(self, label: int) -> List[int]:
        """
        Interview explanation:
        In a normal heap-labeled tree parent = label//2. Zigzag swaps order on
        even levels, so the "real" parent of a zigzag label is the mirror of
        label//2 in that level: level_max + level_min - label//2.

        Algorithm:
        - Find level of label (2^level ≤ label < 2^{level+1}).
        - While label>1: prepend; parent_normal = label//2; mirror parent;
          decrement level.

        Complexity: O(log label) time/space.
        """
        level = 0
        while (1 << (level + 1)) <= label:
            level += 1
        path = []
        while label >= 1:
            path.append(label)
            if label == 1:
                break
            level -= 1
            # parent in normal labeling, then mirror into zigzag level
            parent = label // 2
            level_min = 1 << level
            level_max = (1 << (level + 1)) - 1
            label = level_max + level_min - parent
        path.reverse()
        return path
# @lc code=end
