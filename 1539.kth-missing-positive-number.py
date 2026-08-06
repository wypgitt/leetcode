#
# @lc app=leetcode id=1539 lang=python3
#
# [1539] Kth Missing Positive Number
#
# https://leetcode.com/problems/kth-missing-positive-number/description/
#
# algorithms
# Easy (63.44%)
# Likes:    8029
# Dislikes: 579
# Total Accepted:    845.2K
# Total Submissions: 1.3M
# Testcase Example:  '[2,3,4,7,11]\n5'
#
# Given an array arr of positive integers sorted in a strictly increasing
# order, and an integer k.
# 
# Return the k^th positive integer that is missing from this array.
# 
# 
# Example 1:
# 
# 
# Input: arr = [2,3,4,7,11], k = 5
# Output: 9
# Explanation: The missing positive integers are [1,5,6,8,9,10,12,13,...]. The
# 5^th missing positive integer is 9.
# 
# 
# Example 2:
# 
# 
# Input: arr = [1,2,3,4], k = 2
# Output: 6
# Explanation: The missing positive integers are [5,6,7,...]. The 2^nd missing
# positive integer is 6.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= arr.length <= 1000
# 1 <= arr[i] <= 1000
# 1 <= k <= 1000
# arr[i] < arr[j] for 1 <= i < j <= arr.length
# 
# 
# 
# Follow up:
# 
# Could you solve this problem in less than O(n) complexity?
# 
#

"""
Optimal approach: binary search on the missing-count function.

The array is sorted and strictly increasing. That structure lets us compute how
many positive integers are missing before any index.

For index i:
    arr[i] is the actual value at position i.
    If no numbers were missing, the value at index i would be i + 1.

Therefore:
    missing_before_or_at_i = arr[i] - (i + 1)

Example:
    arr = [2, 3, 4, 7, 11]

    index 0, value 2:
        expected value without missing numbers = 1
        missing count = 2 - 1 = 1
        missing numbers so far: [1]

    index 3, value 7:
        expected value without missing numbers = 4
        missing count = 7 - 4 = 3
        missing numbers so far: [1, 5, 6]

Key observation:
    missing(i) = arr[i] - i - 1 is monotonic nondecreasing.

That means we can binary search for the first index where:
    missing(i) >= k

After the binary search:
    left is the number of array elements that are <= the answer.

Among the first answer positive integers:
    - left numbers are present in arr
    - k numbers are missing

So:
    answer = left + k

Why answer = left + k works:
    Suppose the kth missing number is x. Before or at x, there are exactly k
    missing numbers and exactly left present numbers from arr. Therefore the
    count of positive integers up to x is left + k, so x = left + k.

Algorithm:
    1. Binary search over indices [0, len(arr)].
    2. If missing(mid) < k, the kth missing number is to the right.
    3. Otherwise, it is at or before mid.
    4. Return left + k.

Complexity:
    Time:  O(log n)
        Binary search over the array.

    Space: O(1)
        Only a few variables are used.
"""

# @lc code=start
from typing import List


class Solution:
    def findKthPositive(self, arr: List[int], k: int) -> int:
        left, right = 0, len(arr)

        while left < right:
            mid = (left + right) // 2
            missing = arr[mid] - mid - 1

            if missing < k:
                left = mid + 1
            else:
                right = mid

        return left + k
# @lc code=end
