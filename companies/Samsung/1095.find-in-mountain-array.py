#
# @lc app=leetcode id=1095 lang=python3
#
# [1095] Find in Mountain Array
#
# https://leetcode.com/problems/find-in-mountain-array/description/
#
# algorithms
# Hard (41.89%)
# Likes:    3648
# Dislikes: 156
# Total Accepted:    216K
# Total Submissions: 515K
# Testcase Example:  "[1,2,3,4,5,3,1]"
#
# (This problem is an interactive problem.)
#
# You may recall that an array arr is a mountain array if and only if:
#
# arr.length >= 3
#
# There exists some i with 0 < i < arr.length - 1 such that:
#
# arr[0] < arr[1] < ... < arr[i - 1] < arr[i]
#
# arr[i] > arr[i + 1] > ... > arr[arr.length - 1]
#
# Given a mountain array mountainArr, return the minimum index such that
# mountainArr.get(index) == target. If such an index does not exist, return -1.
#
# You cannot access the mountain array directly. You may only access the array
# using a MountainArray interface:
#
# MountainArray.get(k) returns the element of the array at index k (0-indexed).
#
# MountainArray.length() returns the length of the array.
#
# Submissions making more than 100 calls to MountainArray.get will be judged
# Wrong Answer. Also, any solutions that attempt to circumvent the judge will
# result in disqualification.
#
# Example 1:
#
# Input: mountainArr = [1,2,3,4,5,3,1], target = 3
# Output: 2
# Explanation: 3 exists in the array, at index=2 and index=5. Return the
# minimum index, which is 2.
#
# Example 2:
#
# Input: mountainArr = [0,1,2,4,2,1], target = 3
# Output: -1
# Explanation: 3 does not exist in the array, so we return -1.
#
# Constraints:
#
# 3 <= mountainArr.length() <= 10^4
#
# 0 <= target <= 10^9
#
# 0 <= mountainArr.get(index) <= 10^9
#

# @lc code=start
# """
# This is MountainArray's API interface.
# You should not implement it, or speculate about its implementation
# """
# class MountainArray:
#    def get(self, index: int) -> int:
#    def length(self) -> int:


class Solution:
    def findInMountainArray(self, target: int, mountainArr: "MountainArray") -> int:
        """
        Interview explanation:
        Interactive mountain array: find peak, then binary-search the ascending
        left side for target, then descending right side. Return smallest index.

        Algorithm (3 binary searches):
        - Peak: while lo<hi, mid; if get(mid)<get(mid+1): lo=mid+1 else hi=mid.
        - Left [0..peak]: standard ascending binary search.
        - Right [peak..n-1]: descending binary search.

        Complexity: O(log n) gets, O(1) extra space.
        """
        n = mountainArr.length()
        peak = self._peak_binary(mountainArr, n)
        idx = self._bin_asc(mountainArr, target, 0, peak)
        if idx != -1:
            return idx
        return self._bin_desc(mountainArr, target, peak, n - 1)

    def findInMountainArray_ternary_peak(
        self, target: int, mountainArr: "MountainArray"
    ) -> int:
        """
        Interview explanation:
        Alternate peak finding via ternary search on the unimodal array, then
        the same two binary searches on the flanks.

        Algorithm (ternary + binary):
        - While hi-lo>2: m1,m2 thirds; move toward the larger side.
        - Peak = argmax of remaining window; then binsearch both sides.

        Complexity: O(log n) gets, O(1) extra space.
        """
        n = mountainArr.length()
        lo, hi = 0, n - 1
        while hi - lo > 2:
            m1 = lo + (hi - lo) // 3
            m2 = hi - (hi - lo) // 3
            if mountainArr.get(m1) < mountainArr.get(m2):
                lo = m1
            else:
                hi = m2
        peak = lo
        for i in range(lo, hi + 1):
            if mountainArr.get(i) > mountainArr.get(peak):
                peak = i
        idx = self._bin_asc(mountainArr, target, 0, peak)
        if idx != -1:
            return idx
        return self._bin_desc(mountainArr, target, peak, n - 1)

    def _peak_binary(self, mountainArr: "MountainArray", n: int) -> int:
        lo, hi = 0, n - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if mountainArr.get(mid) < mountainArr.get(mid + 1):
                lo = mid + 1
            else:
                hi = mid
        return lo

    def _bin_asc(self, mountainArr: "MountainArray", target: int, lo: int, hi: int) -> int:
        while lo <= hi:
            mid = (lo + hi) // 2
            val = mountainArr.get(mid)
            if val == target:
                return mid
            if val < target:
                lo = mid + 1
            else:
                hi = mid - 1
        return -1

    def _bin_desc(self, mountainArr: "MountainArray", target: int, lo: int, hi: int) -> int:
        while lo <= hi:
            mid = (lo + hi) // 2
            val = mountainArr.get(mid)
            if val == target:
                return mid
            if val > target:
                lo = mid + 1
            else:
                hi = mid - 1
        return -1
# @lc code=end
