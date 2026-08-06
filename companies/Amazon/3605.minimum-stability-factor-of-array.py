#
# @lc app=leetcode id=3605 lang=python3
#
# [3605] Minimum Stability Factor of Array
#
# https://leetcode.com/problems/minimum-stability-factor-of-array/description/
#
# algorithms
# Hard (21.02%)
# Likes:    41
# Dislikes: 2
# Total Accepted:    4.3K
# Total Submissions: 20.4K
# Testcase Example:  "[3,5,10]\n1"
#
#
# You are given an integer array nums and an integer maxC.
#
# A subarray is called stable if the highest common factor (HCF) of all
# its elements is greater than or equal to 2.
#
# The stability factor of an array is defined as the length of its longest
# stable subarray.
#
# You may modify at most maxC elements of the array to any integer.
#
# Return the minimum possible stability factor of the array after at most
# maxC modifications. If no stable subarray remains, return 0.
#
# Note:
#
# The highest common factor (HCF) of an array is the largest integer that
# evenly divides all the array elements.
#
# A subarray of length 1 is stable if its only element is greater than or
# equal to 2, since HCF([x]) = x.
#
# Example 1:
#
# Input: nums = [3,5,10], maxC = 1
#
# Output: 1
#
# Explanation:
#
# The stable subarray [5, 10] has HCF = 5, which has a stability factor of
# 2.
#
# Since maxC = 1, one optimal strategy is to change nums[1] to 7,
# resulting in nums = [3, 7, 10].
#
# Now, no subarray of length greater than 1 has HCF >= 2. Thus, the
# minimum possible stability factor is 1.
#
# Example 2:
#
# Input: nums = [2,6,8], maxC = 2
#
# Output: 1
#
# Explanation:
#
# The subarray [2, 6, 8] has HCF = 2, which has a stability factor of 3.
#
# Since maxC = 2, one optimal strategy is to change nums[1] to 3 and
# nums[2] to 5, resulting in nums = [2, 3, 5].
#
# Now, no subarray of length greater than 1 has HCF >= 2. Thus, the
# minimum possible stability factor is 1.
#
# Example 3:
#
# Input: nums = [2,4,9,6], maxC = 1
#
# Output: 2
#
# Explanation:
#
# The stable subarrays are:
#
# [2, 4] with HCF = 2 and stability factor of 2.
#
# [9, 6] with HCF = 3 and stability factor of 2.
#
# Since maxC = 1, the stability factor of 2 cannot be reduced due to two
# separate stable subarrays. Thus, the minimum possible stability factor
# is 2.
#
# Constraints:
#
# 1 <= n == nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# 0 <= maxC <= n
#

# @lc code=start

from math import gcd
from typing import List


class Solution:
    def minStable(self, nums: List[int], maxC: int) -> int:
        """
        Interview explanation:
        Stability factor = longest subarray with GCD ≥ 2. Minimize it after
        ≤ maxC changes (change an element to break GCD).

        Algorithm:
        - Binary search answer L. check(L): greedy count of changes needed
          to eliminate every length-L window with range-GCD ≥ 2 (sparse table).
        - If more than maxC changes are required, L is unavoidable.
        - Answer = max L that still cannot be eliminated (0 if none).

        Complexity: O(n log n · log A) preprocess + O(n log n) search.
        """
        n = len(nums)
        log = [0] * (n + 1)
        for i in range(2, n + 1):
            log[i] = log[i // 2] + 1
        kmax = log[n] + 1
        st = [nums[:]]
        for k in range(1, kmax):
            prev = st[k - 1]
            span = 1 << (k - 1)
            cur = [0] * (n - (1 << k) + 1)
            for i in range(len(cur)):
                cur[i] = gcd(prev[i], prev[i + span])
            st.append(cur)

        def range_gcd(l: int, r: int) -> int:
            j = log[r - l + 1]
            return gcd(st[j][l], st[j][r - (1 << j) + 1])

        def cannot_eliminate(length: int) -> bool:
            cnt = 0
            i = 0
            while i + length - 1 < n:
                if range_gcd(i, i + length - 1) >= 2:
                    cnt += 1
                    i += length
                else:
                    i += 1
            return cnt > maxC

        lo, hi, ans = 1, n, 0
        while lo <= hi:
            mid = (lo + hi) // 2
            if cannot_eliminate(mid):
                ans = mid
                lo = mid + 1
            else:
                hi = mid - 1
        return ans
# @lc code=end
