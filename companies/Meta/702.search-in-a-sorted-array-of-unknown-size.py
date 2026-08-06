#
# @lc app=leetcode id=702 lang=python3
#
# [702] Search in a Sorted Array of Unknown Size
#
# https://leetcode.com/problems/search-in-a-sorted-array-of-unknown-size/description/
#
# algorithms
# Medium (73.14%)
# Likes:    942
# Dislikes: 51
# Total Accepted:    114.4K
# Total Submissions: 156.4K
# Testcase Example:  "[-1,0,3,5,9,12]\n9"
#
#
# This is an interactive problem.
#
# You have a sorted array of unique elements and an unknown size. You do
# not have an access to the array but you can use the ArrayReader
# interface to access it. You can call ArrayReader.get(i) that:
#
# returns the value at the i^th index (0-indexed) of the secret array
# (i.e., secret[i]), or
#
# returns 2^31 - 1 if the i is out of the boundary of the array.
#
# You are also given an integer target.
#
# Return the index k of the hidden array where secret[k] == target or
# return -1 otherwise.
#
# You must write an algorithm with O(log n) runtime complexity.
#
# Example 1:
#
# Input: secret = [-1,0,3,5,9,12], target = 9
# Output: 4
# Explanation: 9 exists in secret and its index is 4.
#
# Example 2:
#
# Input: secret = [-1,0,3,5,9,12], target = 2
# Output: -1
# Explanation: 2 does not exist in secret so return -1.
#
# Constraints:
#
# 1 <= secret.length <= 10^4
#
# -10^4 <= secret[i], target <= 10^4
#
# secret is sorted in a strictly increasing order.
#
# @lc code=start
try:
    ArrayReader
except NameError:

    class ArrayReader:
        def get(self, index: int) -> int:
            return 2**31 - 1


class Solution:
    def search(self, reader: "ArrayReader", target: int) -> int:
        """
        Interview explanation:
        Premium: sorted array of unknown size via ArrayReader.get(i) (INT_MAX
        if out of range). Exponentially expand right bound, then binary search.

        Algorithm:
        - lo, hi = 0, 1; while reader.get(hi) < target: lo=hi; hi*=2.
        - Binary search in [lo, hi] for target; return index or -1.

        Complexity: O(log T) time where T is target index, O(1) space.
        """
        if reader.get(0) == target:
            return 0
        lo, hi = 0, 1
        while reader.get(hi) < target:
            lo = hi
            hi <<= 1
        while lo <= hi:
            mid = (lo + hi) // 2
            val = reader.get(mid)
            if val == target:
                return mid
            if val > target:
                hi = mid - 1
            else:
                lo = mid + 1
        return -1
# @lc code=end
