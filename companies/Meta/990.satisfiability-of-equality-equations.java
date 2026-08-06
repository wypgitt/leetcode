/*
 * @lc app=leetcode id=990 lang=java
 *
 * [990] Satisfiability Of Equality Equations
 */

/*
 * --- Interview notes (equality graph, DSU, two-pass order, complexity, edges, alternatives) ---
 *
 * Problem
 * Equations over lowercase variables **`a…z`**, each of form **`"x==y"`** or **`"x!=y"`**. Decide whether there exists an
 * assignment of integers to variables satisfying **all** equations simultaneously.
 *
 * Structure
 * **`==`** is an **equivalence relation** (transitive closure): variables partition into connected components that must share
 * the same value. **`!=`** forbids two variables from sharing a value — feasible iff those two lie in **different** DSU
 * components **after** merging all **`==`** edges.
 *
 * Why Union–Find (Disjoint Set Union)
 * Dynamic connectivity under **`union`** + **`same-set`** queries matches DSU’s API in **α(n)** amortized time per op with
 * path compression (and union-by-rank/size optional).
 *
 * Algorithm — **two passes** (order matters)
 * 1. **First pass — only `==`:** For each **`x==y`**, **`union(x, y)`** so all chains of equality collapse to components.
 * 2. **Second pass — only `!=`:** For each **`x!=y`**, if **`find(x) == find(y)`**, two allegedly distinct values are forced
 *    equal ⇒ **contradiction** ⇒ return **`False`**.
 * If no contradiction, return **`True`**.
 *
 * Parsing 4-character strings
 * • **`"a==b"`** — indices **`0`** and **`3`** are variables; **`s[1] == '='`** distinguishes from **`!=`**.
 * • **`"a!=b"`** — **`s[1] == '!'`** for inequality lines.
 *
 * Data structures
 * **`parent[26]`** (only **`a…z`** appear) — map **`chr → index`** via **`ord(c) - ord('a')`**. Optional **`rank`** array for
 * union-by-rank.
 *
 * Time complexity **O(L · α(26)) ≈ O(L)`** for **`L = len(equations)`** — effectively **O(L)**.
 *
 * Space complexity **O(1)** extra (**26** parents; alphabet fixed).
 *
 * Edge cases
 * • **`x!=x`** — same letter compared unequal; after empty unions, **`find(x)==find(x)`** ⇒ **unsatisfiable** ⇒ **`False`**.
 * • Only **`==`** — always satisfiable (pick one value per component).
 * • Contradictory chain **`a==b`**, **`b==c`**, **`a!=c`** — DSU merges **`a,b,c`** then **`!=`** fails.
 *
 * Tests (statement-style)
 * • **`["a==b","b!=a"]`** → **`False`**.
 * • **`["b==a","a==b"]`** → **`True`**.
 *
 * Alternatives
 * • **Graph coloring / BFS** on constraint graph — heavier; DSU is the canonical linear-time solution for this formulation.
 *
 * --- end notes ---
 */

// @lc code=start
class Solution {
    private int[] parent = new int[26];

    private int find(int x) {
        while (parent[x] != x) {
            parent[x] = parent[parent[x]];
            x = parent[x];
        }
        return x;
    }

    private void union(int a, int b) {
        int ra = find(a);
        int rb = find(b);
        if (ra != rb) {
            parent[ra] = rb;
        }
    }

    private int ix(char c) {
        return c - 'a';
    }

    public boolean equationsPossible(String[] equations) {
        for (int i = 0; i < 26; i++) {
            parent[i] = i;
        }
        for (String e : equations) {
            if (e.charAt(1) == '=') {
                union(ix(e.charAt(0)), ix(e.charAt(3)));
            }
        }
        for (String e : equations) {
            if (e.charAt(1) == '!') {
                if (find(ix(e.charAt(0))) == find(ix(e.charAt(3)))) {
                    return false;
                }
            }
        }
        return true;
    }
}
// @lc code=end
