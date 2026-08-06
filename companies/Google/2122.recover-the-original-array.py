#
# @lc app=leetcode id=2122 lang=python3
#
# [2122] Recover the Original Array
#
# https://leetcode.com/problems/recover-the-original-array/description/
#
# algorithms
# Hard (41.83%)
# Likes:    395
# Dislikes: 34
# Total Accepted:    14.5K
# Total Submissions: 34.7K
# Testcase Example:  "[2,10,6,4,8,12]"
#
# Alice had a 0-indexed array arr consisting of n positive integers. She chose
# an arbitrary positive integer k and created two new 0-indexed integer arrays
# lower and higher in the following manner:
#
#
# lower[i] = arr[i] - k, for every index i where 0 <= i < n
#
#
# higher[i] = arr[i] + k, for every index i where 0 <= i < n
#
# Unfortunately, Alice lost all three arrays. However, she remembers the
# integers that were present in the arrays lower and higher, but not the array
# each integer belonged to. Help Alice and recover the original array.
#
# Given an array nums consisting of 2n integers, where exactly n of the integers
# were present in lower and the remaining in higher, return the original array
# arr. In case the answer is not unique, return any valid array.
#
# Note: The test cases are generated such that there exists at least one valid
# array arr.
#
#
#
# Example 1:
#
# Input: nums = [2,10,6,4,8,12]
# Output: [3,7,11]
# Explanation:
# If arr = [3,7,11] and k = 1, we get lower = [2,6,10] and higher = [4,8,12].
# Combining lower and higher gives us [2,6,10,4,8,12], which is a permutation of
# nums.
# Another valid possibility is that arr = [5,7,9] and k = 3. In that case, lower
# = [2,4,6] and higher = [8,10,12].
#
# Example 2:
#
# Input: nums = [1,1,3,3]
# Output: [2,2]
# Explanation:
# If arr = [2,2] and k = 1, we get lower = [1,1] and higher = [3,3].
# Combining lower and higher gives us [1,1,3,3], which is equal to nums.
# Note that arr cannot be [1,3] because in that case, the only possible way to
# obtain [1,1,3,3] is with k = 0.
# This is invalid since k must be positive.
#
# Example 3:
#
# Input: nums = [5,435]
# Output: [220]
# Explanation:
# The only possible combination is arr = [220] and k = 215. Using them, we get
# lower = [5] and higher = [435].
#
#
#
# Constraints:
#
#
# 2 * n == nums.length
#
#
# 1 <= n <= 1000
#
#
# 1 <= nums[i] <= 10^9
#
#
# The test cases are generated such that there exists at least one valid array
# arr.
#


# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def recoverArray(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        nums is concatenation of arr[i]+k and arr[i]-k for unknown k>0.
        Recover arr (any valid).

        Algorithm:
        - Sort nums. Smallest is some arr[j]-k. Candidate 2k = nums[i]-nums[0]
          for each i; try each even positive diff.
        - Greedily pair via multiset: for each unused low, need low+2k present.

        Complexity: O(n^2) time typical (n<=1000), O(n) space.
        """
        nums = sorted(nums)
        n = len(nums)
        for i in range(1, n):
            diff = nums[i] - nums[0]
            if diff == 0 or diff % 2:
                continue
            k2 = diff  # 2k
            cnt = Counter(nums)
            arr = []
            ok = True
            for x in nums:
                if cnt[x] == 0:
                    continue
                if cnt[x + k2] == 0:
                    ok = False
                    break
                cnt[x] -= 1
                cnt[x + k2] -= 1
                arr.append(x + k2 // 2)
            if ok and len(arr) == n // 2:
                return arr
        return []
# @lc code=end

