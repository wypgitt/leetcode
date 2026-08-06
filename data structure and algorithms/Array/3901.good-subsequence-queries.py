#
# @lc app=leetcode id=3901 lang=python3
#
# [3901] Good Subsequence Queries
#
# https://leetcode.com/problems/good-subsequence-queries/description/
#
# algorithms
# Hard (20.63%)
# Likes:    43
# Dislikes: 1
# Total Accepted:    3.5K
# Total Submissions: 16.9K
# Testcase Example:  "[4,8,12,16]\n2\n[[0,3],[2,6]]"
#
#
# You are given an integer array nums of length n and an integer p.
#
# A non-empty subsequence of nums is called good if:
#
# Its length is strictly less than n.
#
# The greatest common divisor (GCD) of its elements is exactly p.
#
# You are also given a 2D integer array queries of length q, where each
# queries[i] = [ind_i, val_i] indicates that you should update nums[ind_i]
# to val_i.
#
# After each query, determine whether there exists any good subsequence in
# the current array.
#
# Return the number of queries for which a good subsequence exists.
#
# The term gcd(a, b) denotes the greatest common divisor of a and b.
#
# Example 1:
#
# Input: nums = [4,8,12,16], p = 2, queries = [[0,3],[2,6]]
#
# Output: 1
#
# Explanation:
#
#                         i
#                         [ind_i, val_i]
#                         Operation
#                         Updated nums
#                         Any good Subsequence
#
#                         0
#                         [0, 3]
#                         Update nums[0] to 3
#                         [3, 8, 12, 16]
#                         No, as no subsequence has GCD exactly p = 2
#
#                         1
#                         [2, 6]
#                         Update nums[2] to 6
#                         [3, 8, 6, 16]
#                         Yes, subsequence [8, 6] has GCD exactly p = 2
#
# Thus, the answer is 1.
#
# Example 2:
#
# Input: nums = [4,5,7,8], p = 3, queries = [[0,6],[1,9],[2,3]]
#
# Output: 2
#
# Explanation:
#
#                         i
#                         [ind_i, val_i]
#                         Operation
#                         Updated nums
#                         Any good Subsequence
#
#                         0
#                         [0, 6]
#                         Update nums[0] to 6
#                         [6, 5, 7, 8]
#                         No, as no subsequence has GCD exactly p = 3
#
#                         1
#                         [1, 9]
#                         Update nums[1] to 9
#                         [6, 9, 7, 8]
#                         Yes, subsequence [6, 9] has GCD exactly p = 3
#
#                         2
#                         [2, 3]
#                         Update nums[2] to 3
#                         [6, 9, 3, 8]
#                         Yes, subsequence [6, 9, 3] has GCD exactly p = 3
#
# Thus, the answer is 2.
#
# Example 3:
#
# Input: nums = [5,7,9], p = 2, queries = [[1,4],[2,8]]
#
# Output: 0
#
# Explanation:
#
#                         i
#                         [ind_i, val_i]
#                         Operation
#                         Updated nums
#                         Any good Subsequence
#
#                         0
#                         [1, 4]
#                         Update nums[1] to 4
#                         [5, 4, 9]
#                         No, as no subsequence has GCD exactly p = 2
#
#                         1
#                         [2, 8]
#                         Update nums[2] to 8
#                         [5, 4, 8]
#                         No, as no subsequence has GCD exactly p = 2
#
# Thus, the answer is 0.
#
# Constraints:
#
# 2 <= n == nums.length <= 5 * 10^4
#
# 1 <= nums[i] <= 5 * 10^4
#
# 1 <= queries.length <= 5 * 10^4
#
# queries[i] = [ind_i, val_i]
#
# 1 <= val_i, p <= 5 * 10^4
#
# 0 <= ind_i <= n - 1
#

# @lc code=start
class Solution:
    MAX_NUMS = 50000
    _FACTORS = None
    _K = None

    @classmethod
    def _precompute(cls):
        if cls._FACTORS is not None:
            return
        factors = [[] for _ in range(cls.MAX_NUMS + 1)]
        curr, k = 1, 0
        for i in range(2, cls.MAX_NUMS + 1):
            if factors[i]:
                continue
            if curr * i <= cls.MAX_NUMS:
                curr *= i
                k += 1
            for j in range(i, cls.MAX_NUMS + 1, i):
                factors[j].append(i)
        cls._FACTORS = factors
        cls._K = k

    def countGoodSubseq(self, nums: list[int], p: int, queries: list[list[int]]) -> int:
        """
        Interview explanation:
        A good subsequence has GCD exactly p and length < n. Equivalent: among
        a_i = nums[i]/p for multiples of p, some nonempty proper-length subset
        has gcd 1 (⇔ no prime divides all a_i, with a special all-n case).

        Algorithm:
        - Track count of multiples of p and, for each prime q, how many a_i
          are divisible by q (via factor lists).
        - After each update, check: ≥1 multiple, no prime covers all; if every
          element is a multiple, try deleting one (or use n > K shortcut).

        Complexity: O((n+q) · ω) with ω = #prime factors.
        """
        self._precompute()
        FACTORS, K = self._FACTORS, self._K
        n = len(nums)
        if n == 1:
            return 0
        mx = max(max(nums), max(v for _, v in queries))
        cnt = [0] * (mx + 1)
        cnt2 = [0] * (n + 1)
        curr = 0

        def update(x: int, d: int) -> None:
            nonlocal curr
            if x % p:
                return
            for q in FACTORS[x // p]:
                cnt2[cnt[q]] -= 1
                cnt[q] += d
                cnt2[cnt[q]] += 1
            curr += d

        def check() -> bool:
            if curr == 0 or cnt2[curr]:
                return False
            if curr != n or n > K:
                return True
            for i in range(n):
                update(nums[i], -1)
                found = cnt2[curr] == 0
                update(nums[i], +1)
                if found:
                    return True
            return False

        for x in nums:
            update(x, +1)
        ans = 0
        for i, x in queries:
            update(nums[i], -1)
            nums[i] = x
            update(nums[i], +1)
            if check():
                ans += 1
        return ans
# @lc code=end
