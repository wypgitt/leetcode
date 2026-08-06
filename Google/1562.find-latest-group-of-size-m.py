#
# @lc app=leetcode id=1562 lang=python3
#
# [1562] Find Latest Group of Size M
#
# https://leetcode.com/problems/find-latest-group-of-size-m/description/
#
# algorithms
# Medium (43.98%)
# Likes:    684
# Dislikes: 146
# Total Accepted:    23.0K
# Total Submissions: 52.3K
# Testcase Example:  "[3,5,1,2,4]"
#
# Given an array arr that represents a permutation of numbers from 1 to n.
#
# You have a binary string of size n that initially has all its bits set to
# zero. At each step i (assuming both the binary string and arr are 1-indexed)
# from 1 to n, the bit at position arr[i] is set to 1.
#
# You are also given an integer m. Find the latest step at which there exists a
# group of ones of length m. A group of ones is a contiguous substring of 1's
# such that it cannot be extended in either direction.
#
# Return the latest step at which there exists a group of ones of length
# exactly m. If no such group exists, return -1.
#
# Example 1:
#
# Input: arr = [3,5,1,2,4], m = 1
# Output: 4
# Explanation:
# Step 1: "00100", groups: ["1"]
# Step 2: "00101", groups: ["1", "1"]
# Step 3: "10101", groups: ["1", "1", "1"]
# Step 4: "11101", groups: ["111", "1"]
# Step 5: "11111", groups: ["11111"]
# The latest step at which there exists a group of size 1 is step 4.
#
# Example 2:
#
# Input: arr = [3,1,5,4,2], m = 2
# Output: -1
# Explanation:
# Step 1: "00100", groups: ["1"]
# Step 2: "10100", groups: ["1", "1"]
# Step 3: "10101", groups: ["1", "1", "1"]
# Step 4: "10111", groups: ["1", "111"]
# Step 5: "11111", groups: ["11111"]
# No group of size 2 exists during any step.
#
# Constraints:
#
# n == arr.length
#
# 1 <= m <= n <= 10^5
#
# 1 <= arr[i] <= n
#
# All integers in arr are distinct.
#

# @lc code=start
from typing import List


class Solution:
    def findLatestStep(self, arr: List[int], m: int) -> int:
        """
        Interview explanation:
        Start with zeros length n; at step i set arr[i] to 1. Track contiguous
        groups of 1s; return latest step when some group has size m (-1 if never).

        Algorithm (length array / union by ends):
        - length[i]=size of group containing position i (1-indexed), 0 if zero.
        - When setting i: left=length[i-1], right=length[i+1]; new=left+right+1.
        - Decrement count of groups of size left/right; increment size new.
        - If count[m]>0 record step.

        Complexity: O(n) time/space.
        """
        n = len(arr)
        length = [0] * (n + 2)
        count = [0] * (n + 1)
        ans = -1
        for step, i in enumerate(arr, 1):
            left, right = length[i - 1], length[i + 1]
            new = left + right + 1
            length[i - left] = length[i + right] = length[i] = new
            count[left] -= 1
            count[right] -= 1
            count[new] += 1
            if count[m] > 0:
                ans = step
        return ans
# @lc code=end

