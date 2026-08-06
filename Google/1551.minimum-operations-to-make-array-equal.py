#
# @lc app=leetcode id=1551 lang=python3
#
# [1551] Minimum Operations to Make Array Equal
#
# https://leetcode.com/problems/minimum-operations-to-make-array-equal/description/
#
# algorithms
# Medium (82.71%)
# Likes:    1508
# Dislikes: 188
# Total Accepted:    121K
# Total Submissions: 146K
# Testcase Example:  "3"
#
# You have an array arr of length n where arr[i] = (2 * i) + 1 for all valid
# values of i (i.e., 0 <= i < n).
#
# In one operation, you can select two indices x and y where 0 <= x, y < n and
# subtract 1 from arr[x] and add 1 to arr[y] (i.e., perform arr[x] -=1 and
# arr[y] += 1). The goal is to make all the elements of the array equal. It is
# guaranteed that all the elements of the array can be made equal using some
# operations.
#
# Given an integer n, the length of the array, return the minimum number of
# operations needed to make all the elements of arr equal.
#
# Example 1:
#
# Input: n = 3
# Output: 2
# Explanation: arr = [1, 3, 5]
# First operation choose x = 2 and y = 0, this leads arr to be [2, 3, 4]
# In the second operation choose x = 2 and y = 0 again, thus arr = [3, 3, 3].
#
# Example 2:
#
# Input: n = 6
# Output: 9
#
# Constraints:
#
# 1 <= n <= 10^4
#

# @lc code=start
class Solution:
    def minOperations(self, n: int) -> int:
        """
        Interview explanation:
        arr[i]=2*i+1. Median/mean target is n. Ops move 1 from a larger to a
        smaller element; total ops equal sum of deficits on the left half:
        1+3+...+(n-1 if even else n) distance to n → n^2//4.

        Algorithm (closed form):
        - Return n*n // 4.

        Complexity: O(1) time, O(1) space.
        """
        return n * n // 4

    def minOperations_loop(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: explicitly sum (n - arr[i]) // 2... actually each op moves
        1 unit; sum how far left half is below n.

        Algorithm:
        - ans=0; for i in 0..n//2-1: ans += n - (2*i+1); return ans.

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        for i in range(n // 2):
            ans += n - (2 * i + 1)
        return ans
# @lc code=end

