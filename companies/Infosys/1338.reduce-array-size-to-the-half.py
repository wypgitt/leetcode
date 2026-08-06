#
# @lc app=leetcode id=1338 lang=python3
#
# [1338] Reduce Array Size to The Half
#
# https://leetcode.com/problems/reduce-array-size-to-the-half/description/
#
# algorithms
# Medium (69.42%)
# Likes:    3381
# Dislikes: 154
# Total Accepted:    239K
# Total Submissions: 344K
# Testcase Example:  "[3,3,3,3,5,5,5,2,2,7]"
#
# You are given an integer array arr. You can choose a set of integers and
# remove all the occurrences of these integers in the array.
#
# Return the minimum size of the set so that at least half of the integers of
# the array are removed.
#
# Example 1:
#
# Input: arr = [3,3,3,3,5,5,5,2,2,7]
# Output: 2
# Explanation: Choosing {3,7} will make the new array [5,5,5,2,2] which has
# size 5 (i.e equal to half of the size of the old array).
# Possible sets of size 2 are {3,5},{3,2},{5,2}.
# Choosing set {2,7} is not possible as it will make the new array
# [3,3,3,3,5,5,5] which has a size greater than half of the size of the old
# array.
#
# Example 2:
#
# Input: arr = [7,7,7,7,7,7]
# Output: 1
# Explanation: The only possible set you can choose is {7}. This will make the
# new array empty.
#
# Constraints:
#
# 2 <= arr.length <= 10^5
#
# arr.length is even.
#
# 1 <= arr[i] <= 10^5
#

# @lc code=start
from collections import Counter
from typing import List


class Solution:
    def minSetSize(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Remove a set of distinct values to delete at least n/2 elements; minimize
        set size. Greedy: remove highest-frequency values first.

        Algorithm:
        - Count frequencies; sort descending; accumulate until >= n/2.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(arr)
        freqs = sorted(Counter(arr).values(), reverse=True)
        removed = 0
        for i, f in enumerate(freqs, 1):
            removed += f
            if removed >= n // 2:
                return i
        return len(freqs)
# @lc code=end

