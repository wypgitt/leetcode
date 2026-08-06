#
# @lc app=leetcode id=1868 lang=python3
#
# [1868] Product of Two Run-Length Encoded Arrays
#
# https://leetcode.com/problems/product-of-two-run-length-encoded-arrays/description/
#
# algorithms
# Medium (59.65%)
# Likes:    416
# Dislikes: 84
# Total Accepted:    64.2K
# Total Submissions: 107.6K
# Testcase Example:  "[[1,3],[2,3]]\n[[6,3],[3,3]]"
#
#
# Run-length encoding is a compression algorithm that allows for an
# integer array nums with many segments of consecutive repeated numbers to
# be represented by a (generally smaller) 2D array encoded. Each
# encoded[i] = [val_i, freq_i] describes the i^th segment of repeated
# numbers in nums where val_i is the value that is repeated freq_i times.
#
# For example, nums = [1,1,1,2,2,2,2,2] is represented by the run-length
# encoded array encoded = [[1,3],[2,5]]. Another way to read this is
# "three 1's followed by five 2's".
#
# The product of two run-length encoded arrays encoded1 and encoded2 can
# be calculated using the following steps:
#
# Expand both encoded1 and encoded2 into the full arrays nums1 and nums2
# respectively.
#
# Create a new array prodNums of length nums1.length and set prodNums[i] =
# nums1[i] * nums2[i].
#
# Compress prodNums into a run-length encoded array and return it.
#
# You are given two run-length encoded arrays encoded1 and encoded2
# representing full arrays nums1 and nums2 respectively. Both nums1 and
# nums2 have the same length. Each encoded1[i] = [val_i, freq_i] describes
# the i^th segment of nums1, and each encoded2[j] = [val_j, freq_j]
# describes the j^th segment of nums2.
#
# Return the product of encoded1 and encoded2.
#
# Note: Compression should be done such that the run-length encoded array
# has the minimum possible length.
#
# Example 1:
#
# Input: encoded1 = [[1,3],[2,3]], encoded2 = [[6,3],[3,3]]
# Output: [[6,6]]
# Explanation: encoded1 expands to [1,1,1,2,2,2] and encoded2 expands to
# [6,6,6,3,3,3].
# prodNums = [6,6,6,6,6,6], which is compressed into the run-length
# encoded array [[6,6]].
#
# Example 2:
#
# Input: encoded1 = [[1,3],[2,1],[3,2]], encoded2 = [[2,3],[3,3]]
# Output: [[2,3],[6,1],[9,2]]
# Explanation: encoded1 expands to [1,1,1,2,3,3] and encoded2 expands to
# [2,2,2,3,3,3].
# prodNums = [2,2,2,6,9,9], which is compressed into the run-length
# encoded array [[2,3],[6,1],[9,2]].
#
# Constraints:
#
# 1 <= encoded1.length, encoded2.length <= 10^5
#
# encoded1[i].length == 2
#
# encoded2[j].length == 2
#
# 1 <= val_i, freq_i <= 10^4 for each encoded1[i].
#
# 1 <= val_j, freq_j <= 10^4 for each encoded2[j].
#
# The full arrays that encoded1 and encoded2 represent are the same
# length.
#
# @lc code=start
from typing import List


class Solution:
    def findRLEArray(self, encoded1: List[List[int]], encoded2: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        Premium: two RLE arrays [val, freq]; return RLE of elementwise products
        of the decoded arrays (same length). Two-pointer merge on segments.

        Algorithm (two pointers):
        - i=j=0; while both: take m=min(f1,f2); prod=v1*v2; append/merge with
          last if same val; decrease local freqs; advance exhausted pointer.

        Complexity: O(len1+len2) time, O(output) space.
        """
        i = j = 0
        f1 = f2 = 0
        v1 = v2 = 0
        ans = []
        n1, n2 = len(encoded1), len(encoded2)
        while i < n1 or f1:
            if f1 == 0:
                v1, f1 = encoded1[i]
                i += 1
            if f2 == 0:
                if j >= n2:
                    break
                v2, f2 = encoded2[j]
                j += 1
            m = min(f1, f2)
            prod = v1 * v2
            if ans and ans[-1][0] == prod:
                ans[-1][1] += m
            else:
                ans.append([prod, m])
            f1 -= m
            f2 -= m
        return ans
# @lc code=end
