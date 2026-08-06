#
# @lc app=leetcode id=3944 lang=python3
#
# [3944] Minimum Operations to Make Array Modulo Alternating II
#
# https://leetcode.com/problems/minimum-operations-to-make-array-modulo-alternating-ii/description/
#
# algorithms
# Hard (64.55%)
# Likes:    5
# Dislikes: 1
# Total Accepted:    335
# Total Submissions: 519
# Testcase Example:  "[1,4,2,8]\n3"
#
#
# You are given an integer array nums and an integer k.
#
# In one operation, you can increase or decrease any element of nums by 1.
#
# An array is called modulo alternating if there exist two distinct
# integers x and y (0 <= x, y < k) such that:
#
# For every even index i, nums[i] % k == x
#
# For every odd index i, nums[i] % k == y
#
# Return the minimum number of operations required to make nums modulo
# alternating.
#
# Example 1:
#
# Input: nums = [1,4,2,8], k = 3
#
# Output: 2
#
# Explanation:
#
# Let's choose x = 1 for even indices and y = 2 for odd indices.
#
# Perform the following operations:
#
# Increment nums[1] = 4 by 1, giving nums = [1, 5, 2, 8].
#
# Decrement nums[2] = 2 by 1, giving nums = [1, 5, 1, 8].
#
# Now, for even indices, nums[i] % k = 1, and for odd indices, nums[i] % k
# = 2.
#
# Thus, the total number of operations required is 2.
#
# Example 2:
#
# Input: nums = [1,1,1], k = 3
#
# Output: 1
#
# Explanation:
#
# Incrementing nums[1] by 1 gives nums = [1, 2, 1], which satisfies the
# condition with x = 1 and y = 2.
#
# Thus, the total number of operations required is 1.
#
# Example 3:
#
# Input: nums = [6,7,8], k = 2
#
# Output: 0
#
# Explanation:
#
# The array already satisfies the condition with x = 0 and y = 1. Thus, no
# operations are required.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# 2 <= k <= 10^5
#

# @lc code=start
import cmath


class Solution:
    def minOperations(self, nums: list[int], k: int) -> int:
        """
        Interview explanation:
        Pick distinct residues (x, y) for even/odd indices. Cost of a residue
        target is circular distance on Z/kZ; minimize ce[x]+co[y], x≠y.

        Algorithm:
        - Build even/odd residue frequencies.
        - Circular-convolve with w[d]=min(d,k-d) via FFT to get all target costs.
        - Pair each even target with the best odd target of a different residue.

        Complexity: O(n + k log k) time, O(k) space.
        """
        fe = [0] * k
        fo = [0] * k
        for i, v in enumerate(nums):
            if i & 1:
                fo[v % k] += 1
            else:
                fe[v % k] += 1

        def all_costs(freq: list[int]) -> list[int]:
            w = [min(d, k - d) for d in range(k)]
            nfft = 1
            while nfft < 2 * k:
                nfft <<= 1

            def fft(a: list[complex], invert: bool = False) -> None:
                nloc = len(a)
                j = 0
                for i in range(1, nloc):
                    bit = nloc >> 1
                    while j & bit:
                        j ^= bit
                        bit >>= 1
                    j ^= bit
                    if i < j:
                        a[i], a[j] = a[j], a[i]
                length = 2
                while length <= nloc:
                    ang = (2j * cmath.pi / length) * (-1 if invert else 1)
                    wlen = cmath.exp(ang)
                    for i in range(0, nloc, length):
                        wcur = 1 + 0j
                        for j in range(i, i + length // 2):
                            u, v = a[j], a[j + length // 2] * wcur
                            a[j], a[j + length // 2] = u + v, u - v
                            wcur *= wlen
                    length <<= 1
                if invert:
                    for i in range(nloc):
                        a[i] /= nloc

            fa = [complex(x) for x in freq] + [0j] * (nfft - k)
            fb = [complex(x) for x in w] + [0j] * (nfft - k)
            fft(fa)
            fft(fb)
            for i in range(nfft):
                fa[i] *= fb[i]
            fft(fa, True)
            res = [0] * k
            for i in range(nfft):
                res[i % k] += fa[i].real
            return [int(round(x)) for x in res]

        ce, co = all_costs(fe), all_costs(fo)
        min_o = min(co)
        arg_o = co.index(min_o)
        min_o2 = min((co[j] for j in range(k) if j != arg_o), default=0)
        return min(ce[i] + (min_o2 if i == arg_o else min_o) for i in range(k))
# @lc code=end
