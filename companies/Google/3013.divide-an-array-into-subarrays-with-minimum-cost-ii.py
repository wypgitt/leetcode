#
# @lc app=leetcode id=3013 lang=python3
#
# [3013] Divide an Array Into Subarrays With Minimum Cost II
#
# https://leetcode.com/problems/divide-an-array-into-subarrays-with-minimum-cost-ii/description/
#
# algorithms
# Hard (54.70%)
# Likes:    555
# Dislikes: 63
# Total Accepted:    74.9K
# Total Submissions: 136.9K
# Testcase Example:  "[1,3,2,6,4,2]\n3\n3"
#
#
# You are given a 0-indexed array of integers nums of length n, and two
# positive integers k and dist.
#
# The cost of an array is the value of its first element. For example, the
# cost of [1,2,3] is 1 while the cost of [3,4,1] is 3.
#
# You need to divide nums into k disjoint contiguous subarrays, such that
# the difference between the starting index of the second subarray and the
# starting index of the kth subarray should be less than or equal to dist.
# In other words, if you divide nums into the subarrays nums[0..(i_1 -
# 1)], nums[i_1..(i_2 - 1)], ..., nums[i_k-1..(n - 1)], then i_k-1 - i_1
# <= dist.
#
# Return the minimum possible sum of the cost of these subarrays.
#
# Example 1:
#
# Input: nums = [1,3,2,6,4,2], k = 3, dist = 3
# Output: 5
# Explanation: The best possible way to divide nums into 3 subarrays is:
# [1,3], [2,6,4], and [2]. This choice is valid because i_k-1 - i_1 is 5 -
# 2 = 3 which is equal to dist. The total cost is nums[0] + nums[2] +
# nums[5] which is 1 + 2 + 2 = 5.
# It can be shown that there is no possible way to divide nums into 3
# subarrays at a cost lower than 5.
#
# Example 2:
#
# Input: nums = [10,1,2,2,2,1], k = 4, dist = 3
# Output: 15
# Explanation: The best possible way to divide nums into 4 subarrays is:
# [10], [1], [2], and [2,2,1]. This choice is valid because i_k-1 - i_1 is
# 3 - 1 = 2 which is less than dist. The total cost is nums[0] + nums[1] +
# nums[2] + nums[3] which is 10 + 1 + 2 + 2 = 15.
# The division [10], [1], [2,2,2], and [1] is not valid, because the
# difference between i_k-1 and i_1 is 5 - 1 = 4, which is greater than
# dist.
# It can be shown that there is no possible way to divide nums into 4
# subarrays at a cost lower than 15.
#
# Example 3:
#
# Input: nums = [10,8,18,9], k = 3, dist = 1
# Output: 36
# Explanation: The best possible way to divide nums into 3 subarrays is:
# [10], [8], and [18,9]. This choice is valid because i_k-1 - i_1 is 2 - 1
# = 1 which is equal to dist.The total cost is nums[0] + nums[1] + nums[2]
# which is 10 + 8 + 18 = 36.
# The division [10], [8,18], and [9] is not valid, because the difference
# between i_k-1 and i_1 is 3 - 1 = 2, which is greater than dist.
# It can be shown that there is no possible way to divide nums into 3
# subarrays at a cost lower than 36.
#
# Constraints:
#
# 3 <= n <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# 3 <= k <= n
#
# k - 2 <= dist <= n - 2
#

# @lc code=start

from typing import List


class Solution:
    def minimumCost(self, nums: List[int], k: int, dist: int) -> int:
        """
        Interview explanation:
        Cost is nums[0] plus k-1 later subarray starts. Valid starts lie in some
        window of length dist+1 on nums[1:], so minimize nums[0] + sum of the
        (k-1) smallest values in a sliding window of size dist+1.

        Algorithm:
        - Coordinate-compress nums[1:], maintain Fenwick trees for frequency and
          value-sum over the current window.
        - Query sum of (k-1) smallest via binary search on rank + prefix sums.
        - Slide the window across nums[1:] and take the minimum.

        Complexity: O(n log n) time, O(n) space.
        """
        a = nums[1:]
        need = k - 1
        vals = sorted(set(a))
        rank = {v: i + 1 for i, v in enumerate(vals)}
        m = len(vals)

        class BIT:
            def __init__(self, n: int):
                self.n = n
                self.c = [0] * (n + 1)

            def update(self, i: int, d: int) -> None:
                while i <= self.n:
                    self.c[i] += d
                    i += i & -i

            def query(self, i: int) -> int:
                s = 0
                while i > 0:
                    s += self.c[i]
                    i -= i & -i
                return s

        bit_cnt, bit_sum = BIT(m), BIT(m)

        def add(x: int, d: int) -> None:
            r = rank[x]
            bit_cnt.update(r, d)
            bit_sum.update(r, d * x)

        def sum_k_smallest(kk: int) -> int:
            lo, hi, ans_rank = 1, m, m
            while lo <= hi:
                mid = (lo + hi) // 2
                if bit_cnt.query(mid) >= kk:
                    ans_rank = mid
                    hi = mid - 1
                else:
                    lo = mid + 1
            prev = bit_cnt.query(ans_rank - 1) if ans_rank > 1 else 0
            prev_sum = bit_sum.query(ans_rank - 1) if ans_rank > 1 else 0
            return prev_sum + (kk - prev) * vals[ans_rank - 1]

        w = dist + 1
        for i in range(min(w, len(a))):
            add(a[i], 1)
        ans = sum_k_smallest(need)
        for i in range(w, len(a)):
            add(a[i], 1)
            add(a[i - w], -1)
            ans = min(ans, sum_k_smallest(need))
        return nums[0] + ans
# @lc code=end
