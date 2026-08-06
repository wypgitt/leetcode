#
# @lc app=leetcode id=2625 lang=python3
#
# [2625] Flatten Deeply Nested Array
#
# https://leetcode.com/problems/flatten-deeply-nested-array/description/
#
# algorithms
# Medium (66.11%)
# Likes:    431
# Dislikes: 32
# Total Accepted:    86.1K
# Total Submissions: 130.2K
# Testcase Example:  "[1,2,3,[4,5,6],[7,8,[9,10,11],12],[13,14,15]]\n0"
#
# Given a multi-dimensional array arr and a depth n, return a flattened version
# of that array.
#
# A multi-dimensional array is a recursive data structure that contains integers
# or other multi-dimensional arrays.
#
# A flattened array is a version of that array with some or all of the
# sub-arrays removed and replaced with the actual elements in that sub-array.
# This flattening operation should only be done if the current depth of
# nesting is less than n. The depth of the elements in the first array are
# considered to be 0.
#
# Please solve it without the built-in Array.flat method.
#
#
#
# Example 1:
#
# Input
# arr = [1, 2, 3, [4, 5, 6], [7, 8, [9, 10, 11], 12], [13, 14, 15]]
# n = 0
# Output
# [1, 2, 3, [4, 5, 6], [7, 8, [9, 10, 11], 12], [13, 14, 15]]
#
# Explanation
# Passing a depth of n=0 will always result in the original array. This is
# because the smallest possible depth of a subarray (0) is not less than n=0.
# Thus, no subarray should be flattened.
#
# Example 2:
#
# Input
# arr = [1, 2, 3, [4, 5, 6], [7, 8, [9, 10, 11], 12], [13, 14, 15]]
# n = 1
# Output
# [1, 2, 3, 4, 5, 6, 7, 8, [9, 10, 11], 12, 13, 14, 15]
#
# Explanation
# The subarrays starting with 4, 7, and 13 are all flattened. This is because
# their depth of 0 is less than 1. However [9, 10, 11] remains unflattened
# because its depth is 1.
#
# Example 3:
#
# Input
# arr = [[1, 2, 3], [4, 5, 6], [7, 8, [9, 10, 11], 12], [13, 14, 15]]
# n = 2
# Output
# [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
#
# Explanation
# The maximum depth of any subarray is 1. Thus, all of them are flattened.
#
#
#
# Constraints:
#
#
# 0 <= count of numbers in arr <= 10^5
#
#
# 0 <= count of subarrays in arr <= 10^5
#
#
# maxDepth <= 1000
#
#
# -1000 <= each number <= 1000
#
#
# 0 <= n <= 1000
#

# @lc code=start
from typing import Any, List


def flat(arr: List[Any], n: int) -> List[Any]:
    """
    Interview explanation:
    Flatten nested lists up to depth n (elements at depth 0). Depth-n
    nested lists are left intact when remaining depth is 0.

    Algorithm:
    - Recursively walk lists; if remaining depth > 0 and item is a list,
      expand it with depth-1; else append as-is.

    Complexity: O(total elements) time and space.
    """
    def helper(items: List[Any], depth: int) -> List[Any]:
        """
        Interview explanation:
        Recursive flatten with remaining depth budget.

        Algorithm:
        - Expand lists while depth > 0; otherwise keep nested structure.

        Complexity: O(size of subtree).
        """
        out: List[Any] = []
        for item in items:
            if isinstance(item, list) and depth > 0:
                out.extend(helper(item, depth - 1))
            else:
                out.append(item)
        return out

    return helper(arr, n)


class Solution:
    def flat(self, arr: List[Any], n: int) -> List[Any]:
        """
        Interview explanation:
        Thin Solution wrapper for flat.

        Algorithm:
        - Delegate to flat(arr, n).

        Complexity: O(total elements) time and space.
        """
        return flat(arr, n)
# @lc code=end
