#
# @lc app=leetcode id=805 lang=python3
#
# [805] Split Array With Same Average
#
# https://leetcode.com/problems/split-array-with-same-average/description/
#
# algorithms
# Hard (27.34%)
# Likes:    1367
# Dislikes: 143
# Total Accepted:    49.6K
# Total Submissions: 181K
# Testcase Example:  "[1,2,3,4,5,6,7,8]"
#
# You are given an integer array nums.
#
# You should move each element of nums into one of the two arrays A and B such
# that A and B are non-empty, and average(A) == average(B).
#
# Return true if it is possible to achieve that and false otherwise.
#
# Note that for an array arr, average(arr) is the sum of all the elements of
# arr over the length of arr.
#
# Example 1:
#
# Input: nums = [1,2,3,4,5,6,7,8]
# Output: true
# Explanation: We can split the array into [1,4,5,8] and [2,3,6,7], and both of
# them have an average of 4.5.
#
# Example 2:
#
# Input: nums = [3,1]
# Output: false
#
# Constraints:
#
# 1 <= nums.length <= 30
#
# 0 <= nums[i] <= 10^4
#

# @lc code=start

from typing import List


class Solution:
    def splitArraySameAverage(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Split into nonempty A,B with avg(A)=avg(B) ⇒ avg(A)=avg(whole) ⇒
        sum(A)*n = total*len(A). Meet-in-the-middle: all subset sums of left/
        right halves keyed by size; check for size k=1..n//2 whether needed
        sum exists.

        Algorithm (meet in the middle):
        - total=sum(nums); for k in 1..n//2: if total*k % n==0 check subset
          sum total*k//n of size k via MITM on halves.

        Complexity: O(2^{n/2} * n) time/space.
        """
        n = len(nums)
        if n < 2:
            return False
        total = sum(nums)
        nums = sorted(nums)
        # Early prune: need some k with total*k % n == 0
        possible = False
        for k in range(1, n // 2 + 1):
            if total * k % n == 0:
                possible = True
                break
        if not possible:
            return False

        half = n // 2
        left, right = nums[:half], nums[half:]

        def subset_sums(arr: List[int]) -> List[set]:
            # sums[k] = set of sums with k elements
            m = len(arr)
            sums = [set() for _ in range(m + 1)]
            sums[0].add(0)
            for v in arr:
                for k in range(m, 0, -1):
                    for s in sums[k - 1]:
                        sums[k].add(s + v)
            return sums

        L = subset_sums(left)
        R = subset_sums(right)
        for k in range(1, n // 2 + 1):
            if total * k % n:
                continue
            need = total * k // n
            for i in range(max(0, k - len(right)), min(k, len(left)) + 1):
                j = k - i
                for s in L[i]:
                    if need - s in R[j]:
                        # nonempty proper: k < n already
                        return True
        return False
# @lc code=end
