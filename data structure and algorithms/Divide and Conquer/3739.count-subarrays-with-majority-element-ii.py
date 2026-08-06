#
# @lc app=leetcode id=3739 lang=python3
#
# [3739] Count Subarrays With Majority Element II
#
# https://leetcode.com/problems/count-subarrays-with-majority-element-ii/description/
#
# algorithms
# Hard (64.80%)
# Likes:    314
# Dislikes: 9
# Total Accepted:    76.5K
# Total Submissions: 118K
# Testcase Example:  "[1,2,2,3]\n2"
#
#
# You are given an integer array nums and an integer target.
#
# Return the number of subarrays of nums in which target is the majority
# element.
#
# The majority element of a subarray is the element that appears strictly
# more than half of the times in that subarray.
#
# Example 1:
#
# Input: nums = [1,2,2,3], target = 2
#
# Output: 5
#
# Explanation:
#
# Valid subarrays with target = 2 as the majority element:
#
# nums[1..1] = [2]
#
# nums[2..2] = [2]
#
# nums[1..2] = [2,2]
#
# nums[0..2] = [1,2,2]
#
# nums[1..3] = [2,2,3]
#
# So there are 5 such subarrays.
#
# Example 2:
#
# Input: nums = [1,1,1,1], target = 1
#
# Output: 10
#
# Explanation:
#
# ​​​​​​​All 10 subarrays have 1 as the majority element.
#
# Example 3:
#
# Input: nums = [1,2,3], target = 4
#
# Output: 0
#
# Explanation:
#
# target = 4 does not appear in nums at all. Therefore, there cannot be
# any subarray where 4 is the majority element. Hence the answer is 0.
#
# Constraints:
#
# 1 <= nums.length <= 10^​​​​​​​5
#
# 1 <= nums[i] <= 10^​​​​​​​9
#
# 1 <= target <= 10^9
#

# @lc code=start
from typing import List


class BinaryIndexedTree:
    __slots__ = ("n", "c")

    def __init__(self, n: int):
        self.n = n
        self.c = [0] * (n + 1)

    def update(self, x: int, delta: int) -> None:
        """
        Interview explanation:
        Fenwick point update: add delta at 1-based index x.

        Algorithm:
        - Walk x += x & -x updating fenwick nodes.

        Complexity: O(log n) time.
        """
        while x <= self.n:
            self.c[x] += delta
            x += x & -x

    def query(self, x: int) -> int:
        """
        Interview explanation:
        Fenwick prefix sum on [1..x].

        Algorithm:
        - Walk x -= x & -x accumulating node sums.

        Complexity: O(log n) time.
        """
        s = 0
        while x:
            s += self.c[x]
            x -= x & -x
        return s


class Solution:
    def countMajoritySubarrays(self, nums: List[int], target: int) -> int:
        """
        Interview explanation:
        Treat target as +1 and others as -1. Majority iff subarray sum > 0.
        With prefix sums, count pairs i < j with pref[j] > pref[i] using a BIT.

        Algorithm:
        - Map prefixes from [-n,n] to [1, 2n+1] via offset n+1.
        - For each new prefix s, add query(s-1), then update(s).

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(nums)
        tree = BinaryIndexedTree(2 * n + 1)
        s = n + 1
        tree.update(s, 1)
        ans = 0
        for x in nums:
            s += 1 if x == target else -1
            ans += tree.query(s - 1)
            tree.update(s, 1)
        return ans

    def countMajoritySubarrays_merge(self, nums: List[int], target: int) -> int:
        """
        Interview explanation:
        Alternate: build the +1/-1 prefix array and count strict inversions of
        the opposite kind (later > earlier) via merge sort.

        Algorithm:
        - Pref array; merge-sort count of pairs with left value < right value
          when combining (order by index).

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(nums)
        pref = [0] * (n + 1)
        for i, x in enumerate(nums):
            pref[i + 1] = pref[i] + (1 if x == target else -1)
        ans = 0

        def sort_count(a: List[int]) -> List[int]:
            nonlocal ans
            if len(a) <= 1:
                return a
            mid = len(a) // 2
            left = sort_count(a[:mid])
            right = sort_count(a[mid:])
            i = j = 0
            merged = []
            while i < len(left) and j < len(right):
                if left[i] < right[j]:
                    # left[i] pairs with all remaining right[j..]
                    ans += len(right) - j
                    merged.append(left[i])
                    i += 1
                else:
                    merged.append(right[j])
                    j += 1
            merged.extend(left[i:])
            merged.extend(right[j:])
            return merged

        sort_count(pref)
        return ans
# @lc code=end

