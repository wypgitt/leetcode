#
# @lc app=leetcode id=1299 lang=python3
#
# [1299] Replace Elements with Greatest Element on Right Side
#
# https://leetcode.com/problems/replace-elements-with-greatest-element-on-right-side/description/
#
# algorithms
# Easy (72.47%)
# Likes:    2904
# Dislikes: 271
# Total Accepted:    568K
# Total Submissions: 784K
# Testcase Example:  "[17,18,5,4,6,1]"
#
# Given an array arr, replace every element in that array with the greatest
# element among the elements to its right, and replace the last element with
# -1.
#
# After doing so, return the array.
#
# Example 1:
#
# Input: arr = [17,18,5,4,6,1]
# Output: [18,6,6,6,1,-1]
# Explanation:
# - index 0 --> the greatest element to the right of index 0 is index 1 (18).
# - index 1 --> the greatest element to the right of index 1 is index 4 (6).
# - index 2 --> the greatest element to the right of index 2 is index 4 (6).
# - index 3 --> the greatest element to the right of index 3 is index 4 (6).
# - index 4 --> the greatest element to the right of index 4 is index 5 (1).
# - index 5 --> there are no elements to the right of index 5, so we put -1.
#
# Example 2:
#
# Input: arr = [400]
# Output: [-1]
# Explanation: There are no elements to the right of index 0.
#
# Constraints:
#
# 1 <= arr.length <= 10^4
#
# 1 <= arr[i] <= 10^5
#

# @lc code=start

from typing import List


class Solution:
    def replaceElements(self, arr: List[int]) -> List[int]:
        """
        Interview explanation:
        Replace each element by greatest element to its right; last = -1.
        Scan right-to-left tracking running max.

        Algorithm:
        - mx=-1; for i from n-1..0: arr[i],mx = mx, max(mx, arr[i]).

        Complexity: O(n) time, O(1) extra space.
        """
        mx = -1
        for i in range(len(arr) - 1, -1, -1):
            arr[i], mx = mx, max(mx, arr[i])
        return arr
# @lc code=end
