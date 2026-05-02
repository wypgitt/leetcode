#
# @lc app=leetcode id=3916 lang=python3
#
# [3916] Number of Zig Zag Arrays III
#
# Correctness (odd length exponent): v·T^(2k+1) is NOT vd·(LR)^(k+1)+vu·(RL)^(k+1).
# With T=[[0,L],[R,0]], one gets new D-block = vu·(RL)^k·R and new U-block = vd·(LR)^k·L.
#
# Performance (CP Python):
# - Block reduction: (2m)×(2m) → m×m matrices LR=L·R, RL=R·L (LR[i,j]=min(i,j),
#   RL[i,j]=m−1−max(i,j)).
# - Flat row-major int lists (lower overhead than list-of-lists).
# - Symmetric squaring: if M is symmetric, (M²)[i,j]=Σ_k M[i,k]M[j,k]; fill only
#   i≤j and mirror → ~2× fewer ops when computing cur·cur in binary exponentiation.
# - General multiply kept for nonsymmetric R·cur.
#
# NumPy is intentionally NOT used: modular integer matmul needs big integers or
# per-step `%`, and object-dtype loops are slower than tight Python int loops here.
#
# =============================================================================

# @lc code=start
from typing import List


class Solution:
    MOD = 10**9 + 7

    def zigZagArrays(self, n: int, l: int, r: int) -> int:
        mod = self.MOD
        m = r - l + 1

        if n == 1:
            return m % mod
        if n == 2:
            return (m * (m - 1)) % mod

        ex = n - 2

        Ls = self._build_L_flat(m, mod)
        Rs = self._build_R_flat(m, mod)
        LR = self._build_min_matrix_flat(m, mod)
        RL = self._build_max_matrix_flat(m, mod)

        vd = list(range(m))
        vu = [m - 1 - j for j in range(m)]

        if ex % 2 == 0:
            k = ex // 2
            Plr = self._mat_pow_symmetric_base(LR, m, k, mod)
            Prl = self._mat_pow_symmetric_base(RL, m, k, mod)
            a = self._vec_mat_flat(vd, Plr, m, mod)
            b = self._vec_mat_flat(vu, Prl, m, mod)
        else:
            k = ex // 2
            Plr = self._mat_pow_symmetric_base(LR, m, k, mod)
            Prl = self._mat_pow_symmetric_base(RL, m, k, mod)
            # T^(2k+1) has blocks (LR)^k·L on U<-D and (RL)^k·R on D<-U :
            #   new(D-part) = vu · (RL)^k · R ,   new(U-part) = vd · (LR)^k · L
            tmp_u = self._mat_mul_flat(Prl, Rs, m, mod)
            tmp_d = self._mat_mul_flat(Plr, Ls, m, mod)
            a = self._vec_mat_flat(vu, tmp_u, m, mod)
            b = self._vec_mat_flat(vd, tmp_d, m, mod)

        return (sum(a) + sum(b)) % mod

    def _build_L_flat(self, m: int, mod: int) -> List[int]:
        """D_i → U_j: L[i,j]=1 iff j<i (strict lower 1s in value index)."""
        M = [0] * (m * m)
        for i in range(m):
            base = i * m
            for j in range(i):
                M[base + j] = 1
        return M

    def _build_R_flat(self, m: int, mod: int) -> List[int]:
        """U_i → D_j: R[i,j]=1 iff j>i."""
        M = [0] * (m * m)
        for i in range(m):
            base = i * m
            for j in range(i + 1, m):
                M[base + j] = 1
        return M

    def _build_min_matrix_flat(self, m: int, mod: int) -> List[int]:
        M = [0] * (m * m)
        for i in range(m):
            row = i * m
            for j in range(m):
                M[row + j] = min(i, j) % mod
        return M

    def _build_max_matrix_flat(self, m: int, mod: int) -> List[int]:
        M = [0] * (m * m)
        for i in range(m):
            row = i * m
            for j in range(m):
                M[row + j] = (m - 1 - max(i, j)) % mod
        return M

    def _mat_pow_symmetric_base(self, M: List[int], m: int, p: int, mod: int) -> List[int]:
        """Binary exponentiation; base matrix M is symmetric so use symmetric squaring."""
        R = [0] * (m * m)
        for i in range(m):
            R[i * m + i] = 1
        cur = M[:]
        while p:
            if p & 1:
                R = self._mat_mul_flat(R, cur, m, mod)
            cur = self._symmetric_square_flat(cur, m, mod)
            p //= 2
        return R

    def _symmetric_square_flat(self, M: List[int], m: int, mod: int) -> List[int]:
        """For symmetric M: C[i,j]=Σ_k M[i,k]M[j,k]; compute i≤j only."""
        C = [0] * (m * m)
        for i in range(m):
            ib = i * m
            for j in range(i, m):
                jb = j * m
                s = 0
                for k in range(m):
                    s += M[ib + k] * M[jb + k]
                v = s % mod
                C[ib + j] = v
                if i != j:
                    C[j * m + i] = v
        return C

    def _mat_mul_flat(self, A: List[int], B: List[int], m: int, mod: int) -> List[int]:
        """ikj order (good cache); one `%` per row output cell after summing all k."""
        C = [0] * (m * m)
        for i in range(m):
            ib = i * m
            for k in range(m):
                aik = A[ib + k]
                if aik == 0:
                    continue
                kb = k * m
                for j in range(m):
                    C[ib + j] += aik * B[kb + j]
            for j in range(m):
                C[ib + j] %= mod
        return C

    def _vec_mat_flat(self, v: List[int], M: List[int], m: int, mod: int) -> List[int]:
        out = [0] * m
        for j in range(m):
            s = 0
            sj = j
            for i in range(m):
                vi = v[i]
                if vi:
                    s = (s + vi * M[i * m + sj]) % mod
            out[j] = s
        return out


# @lc code=end
