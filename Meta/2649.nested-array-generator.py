#
# @lc app=leetcode id=2649 lang=python3
#
# [2649] Nested Array Generator
#
# https://leetcode.com/problems/nested-array-generator/description/
#
# algorithms
# Medium (78.12%)
# Likes:    175
# Dislikes: 13
# Total Accepted:    20.3K
# Total Submissions: 26K
# Testcase Example:  "[[[6]],[1,3],[]]"
#
# Given a multi-dimensional array of integers, return a generator object
# which yields integers in the same order as inorder traversal.
#
# A multi-dimensional array is a recursive data structure that contains both
# integers and other multi-dimensional arrays.
#
# inorder traversal iterates over each array from left to right, yielding any
# integers it encounters or applying inorder traversal to any arrays it
# encounters.
#
#
#
# Example 1:
#
# Input: arr = [[[6]],[1,3],[]]
# Output: [6,1,3]
# Explanation:
# const generator = inorderTraversal(arr);
# generator.next().value; // 6
# generator.next().value; // 1
# generator.next().value; // 3
# generator.next().done; // true
#
# Example 2:
#
# Input: arr = []
# Output: []
# Explanation: There are no integers so the generator doesn't yield anything.
#
#
#
# Constraints:
#
#
# 0 <= arr.flat().length <= 10^5
#
#
# 0 <= arr.flat()[i] <= 10^5
#
#
# maxNestingDepth <= 10^5
#
#
#
# Can you solve this without creating a new flattened version of the array?
#

# @lc code=start
from typing import Any, Generator, List, Union

Nested = Union[int, List["Nested"]]


def inorderTraversal(arr: Nested) -> Generator[int, None, None]:
    """
    Interview explanation:
    Generator that yields integers from a nested list structure in inorder
    (left-to-right DFS) without building a flattened copy first.

    Algorithm:
    - Recursively walk: yield ints; for lists, traverse each child in order.

    Complexity: O(n) time over all nodes; O(d) stack for nesting depth d.
    """
    if isinstance(arr, list):
        for item in arr:
            yield from inorderTraversal(item)
    else:
        yield arr


class Solution:
    def inorderTraversal(self, arr: Nested) -> Generator[int, None, None]:
        """
        Interview explanation:
        Thin Solution wrapper for nested-array inorderTraversal.

        Algorithm:
        - Delegate to inorderTraversal(arr).

        Complexity: Same as inorderTraversal.
        """
        return inorderTraversal(arr)
# @lc code=end
