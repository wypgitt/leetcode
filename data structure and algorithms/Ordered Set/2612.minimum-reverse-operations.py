#
# @lc app=leetcode id=2612 lang=python3
#
# [2612] Minimum Reverse Operations
#
# --- Notes (problem, graph model, parity / interval, DSU skip, BFS, complexity, edges, interview) ---
#
# Problem restatement
# Length-n binary array (indices 0..n-1). Exactly one position `p` is 1; all others 0.
# One operation: choose any contiguous subarray of length exactly `k` and reverse it (the single 1
# moves with its element). After each operation, the 1 must NOT lie on any index in `banned`.
# For every index `i`, compute the minimum number of operations to have the 1 at `i`, or -1 if
# impossible. Return an array of length n (answer[p] is always 0).
#
# Graph modeling
# Positions 0..n-1 are states. An undirected edge connects u and v if one reverse of length k can
# send the 1 from u to v in one step (and v to u), while the landing position is not banned.
# All edges have weight 1 -> shortest path = minimum operations -> BFS from source `p`.
#
# Neighbor formula (reverse window [l, l+k-1] containing u)
# After reversing, index u maps to v = l + (l+k-1) - u = 2l + k - 1 - u.
# For fixed u and k, as l runs over integers such that 0 <= l <= n-k and l <= u <= l+k-1,
# we get l in [max(0,u-k+1), min(u, n-k)], and v = 2l + k - 1 - u steps by 2 when l increases by 1.
# So from u you can reach a contiguous range of candidate indices [L, R] that share the same
# parity pattern (step size 2 in index space).
#
# Reachable interval endpoints (equivalent forms appear in editorials)
# With walkccc / kamyu notation:
#   L = max(u - k + 1, k - 1 - u)
#   R = min(u + k - 1, n - 1 - (u - (n - k)))
# Any valid destination index v in one move lies in [L, R] with v ≡ L (mod 2).
#
# Why not naive BFS?
# A single u may have Theta(k) neighbors; dense edges make O(n*k) BFS too slow for large n.
# All neighbors in one move form an arithmetic progression with step 2 inside [L,R]. We must
# enumerate unvisited positions in that range quickly — either:
#   (A) Two ordered sets keyed by parity -> bisect/range delete -> O(log n) per operation, or
#   (B) Disjoint-set “union with next index” + jump pointers -> amortized near O(1) per position.
#
# Algorithm implemented — BFS + Union-Find skip (kamyu / editorial O(n α(n)))
# Maintain DSU over indices 0..n+1 with auxiliary array `right` merged on union:
#   Initially right[i] = i. Idea: indices with same parity link by union(i, i+2); after visiting
#   index x we union(x, x+2) so future iterations skip over filled positions along that parity chain.
# When expanding BFS layer from u:
#   Compute [L, R] for one-step reachable indices (same parity as L).
#   Let x = find_first_available(L) implemented as uf.right_set(L) (depends on DSU state).
#   While x <= R: relax x (if not banned, set answer and push to next layer); ALWAYS union(x, x+2)
#   to remove x from future scans; then x <- uf.right_set(x).
# Start: union(p, p+2) once so the starting slot is skipped like visited along its parity chain.
#
# Banned indices
# Never enqueue them as destinations; still union past them when scanning so we do not stall on
# forbidden cells (kamyu always unions each x encountered in [L,R], but only pushes when not banned).
#
# Time complexity
# - Each index is processed / skipped at most once per parity chain logic -> O(n α(n)) DSU work
#   plus O(n) BFS layers overall -> ~O(n α(n)) ≈ O(n) practically.
#
# Space complexity
# - O(n) for DSU parent/rank/right, answer array, banned flags, queue.
#
# Alternative
# - SortedList / TreeSet per parity: O(n log n), only standard library if you simulate with bisect
#   on sorted arrays is O(n) per delete worst case — not ideal; DSU skip is the LC-friendly choice.
#
# Edge cases
# - k == n: only full-array reverses; limited neighbors.
# - banned contains almost all indices: many -1 entries.
# - p banned is impossible per constraints (usually p not in banned).
#
# LeetCode submission
# Imports must be inside the LC code section markers (otherwise NameError on List at submit).
#
# Interview walkthrough
# 1) Model positions as graph; unweighted shortest path -> BFS.
# 2) Derive neighbor range [L,R] and step-2 structure from reverse formula.
# 3) Accelerate range relaxation with DSU skip list or balanced sets.
# 4) Complexity and parity bookkeeping.
# --- end notes ---

# @lc code=start
from typing import List


class _UnionFind:
    """DSU with merged `right` jump — see header notes."""

    __slots__ = ("parent", "rank", "right")

    def __init__(self, n: int) -> None:
        """
        Interview explanation:
        DSU that also tracks each component’s maximum index (`right`) for
        skipping already-visited parity positions during BFS.

        Algorithm:
        - parent/rank for union-by-rank; right[i] starts as i and grows on merge.

        Complexity: O(n) time and space.
        """
        self.parent = list(range(n))
        self.rank = [0] * n
        self.right = list(range(n))

    def find(self, x: int) -> int:
        stk = []
        while self.parent[x] != x:
            stk.append(x)
            x = self.parent[x]
        while stk:
            self.parent[stk.pop()] = x
        return x

    def union(self, x: int, y: int) -> bool:
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] > self.rank[py]:
            px, py = py, px
        self.parent[px] = py
        if self.rank[px] == self.rank[py]:
            self.rank[py] += 1
        self.right[py] = max(self.right[px], self.right[py])
        return True

    def right_set(self, x: int) -> int:
        return self.right[self.find(x)]


class Solution:
    def minReverseOperations(self, n: int, p: int, banned: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        From a single 1 at index p, each op reverses a length-k subarray. Return min ops
        for the 1 to reach every index (or -1), never landing on banned indices.

        Algorithm:
        - Model positions as an unweighted graph; one reverse from u reaches indices in
          [L, R] with step 2 (same parity as L).
        - BFS from p; accelerate scanning unvisited positions in each [L, R] with a DSU
          that unions visited index x with x+2 so future scans skip filled slots.

        Complexity: O(n α(n)) time, O(n) space.
        """
        banned_on = [False] * n
        for i in banned:
            banned_on[i] = True

        ans = [-1] * n
        ans[p] = 0

        uf = _UnionFind(n + 2)
        uf.union(p, p + 2)

        q = [p]
        step = 1
        while q:
            nxt: List[int] = []
            for u in q:
                left = max(u - k + 1, k - 1 - u)
                right = min(u + k - 1, n - 1 - (u - (n - k)))
                x = uf.right_set(left)
                while x <= right:
                    if not banned_on[x]:
                        ans[x] = step
                        nxt.append(x)
                    uf.union(x, x + 2)
                    x = uf.right_set(x)
            q = nxt
            step += 1

        return ans


# @lc code=end
