/*
 * @lc app=leetcode id=963 lang=java
 *
 * [963] Minimum Area Rectangle Ii
 */

/*
 * --- Interview notes (geometry, hashing diagonals, cross product area, complexity) ---
 *
 * Problem
 * Given **`points`** in the plane, choose **four distinct** points that are the vertices of a **rectangle** (edges not required
 * to be parallel to the axes). Return the **minimum** possible **area**, or **`0`** if no rectangle exists.
 *
 * Geometry — diagonals characterize a rectangle
 * In a **parallelogram**, diagonals **bisect** each other. In a **rectangle**, the two diagonals have **equal length**. So every
 * rectangle gives **two unordered pairs** of points (the two diagonals) that share:
 * • the **same midpoint** (**same bisector point**), and
 * • the **same squared Euclidean length** (**`dist²`** along either diagonal).
 *
 * Conversely, if two **disjoint** segments **PQ** and **RS** share a midpoint and have equal length, their four endpoints form a
 * **parallelogram with equal diagonals**, hence a **rectangle**. So valid rectangles correspond exactly to choosing **two distinct**
 * diagonal-pairs in the same **(midpoint, length²)** class whose four indices are all different.
 *
 * Why group by **(sx, sy, d²)** with **sx = x₁+x₂**, **sy = y₁+y₂**
 * The midpoint is **`((x₁+x₂)/2, (y₁+y₂)/2)`**. Using **integer** **`(x₁+x₂, y₁+y₂)`** avoids floating keys and uniquely fixes the
 * midpoint for integer coordinates. **`d² = (x₁-x₂)²+(y₁-y₂)²`** is the squared diagonal length (same for both diagonals of one
 * rectangle).
 *
 * Area without unstable midpoint arithmetic
 * Let **`D₁ = (xᵢ-xⱼ, yᵢ-yⱼ)`** and **`D₂ = (xₖ-xₗ, yₖ-yₗ)`** be vectors along the two diagonals (same length). If **`O`** is the
 * common midpoint and **`u = Pᵢ-O`**, **`v = Pₖ-O`** are half-diagonals to endpoints **`i`** and **`k`**, then
 * **`area = 2 · |u × v|`** (parallelogram spanned by **`u,v`** from **`O`** covers half the rectangle… standard derivation). Expanding
 * in coordinates yields the **integer-friendly** form:
 *
 * **`area = | (xᵢ-xⱼ)(yₖ-yₗ) - (yᵢ-yⱼ)(xₖ-xₗ) | / 2`**
 *
 * which equals **`| D₁ × D₂ | / 2`** (scalar **2D cross magnitude**). Endpoint order along each diagonal only flips signs → absolute
 * value unchanged.
 *
 * Algorithm
 * 1. Enumerate all unordered pairs **`(i, j)`**, **`i < j`**, append **`(i, j)`** to **`groups[(sx, sy, d²)]`**.
 * 2. For each bucket with **≥ 2** pairs, try every unordered pair of entries **`((i,j), (k,l))`**.
 * 3. If **`|{i,j,k,l}| = 4`**, compute **`area`** via the formula above; track minimum.
 * 4. Return **`0`** if **`n < 4`** or no valid rectangle found.
 *
 * Data structures
 * • **`defaultdict(list)`** — maps a diagonal signature to all pairs that share it (**`O(n²)`** entries total).
 * • No spatial tree needed — algebraic grouping is exact for this characterization.
 *
 * Time complexity
 * **`O(n²)`** pairs enumerated; processing buckets costs **`Σ_k C(m_k, 2)`** where **`m_k`** is bucket sizes. In worst-case patterns
 * many pairs could land in one bucket (**`O(n⁴)`** upper bound), but for typical **`n ≤ 500`** this passes; average random sets spread
 * pairs across buckets.
 *
 * Space complexity **`O(n²)`** for storing all unordered pairs (signature lists).
 *
 * Edge cases
 * • **Fewer than 4 points** — **`0`**.
 * • **Degenerate “rectangle”** (e.g. collinear)** — cross product **`0`**, area **`0`**; minimum might stay **`0`** if only degenerate
 *   configs exist (still consistent with “minimum area”).
 * • **Floating output** — LeetCode expects **`float`**; dividing by **`2.0`** is fine.
 *
 * Tests (sanity)
 * • Square corners **`(0,0),(0,1),(1,0),(1,1)`** → area **`1`**.
 * • **`2×1`** axis-aligned rectangle **`(0,0),(2,0),(2,1),(0,1)`** → area **`2`** (diagonals **`(0,0)-(2,1)`** and **`(0,1)-(2,0)`**).
 *
 * Improvements
 * • **Early pruning** — skip buckets with **`< 2`** pairs.
 * • **Numerical** — integer cross product until final **`/ 2.0`** minimizes FP error.
 *
 * --- end notes ---
 */

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// @lc code=start
class Solution {
    public double minAreaFreeRect(int[][] points) {
        int n = points.length;
        if (n < 4) {
            return 0.0;
        }

        Map<String, List<int[]>> groups = new HashMap<>();
        for (int i = 0; i < n; i++) {
            int xi = points[i][0];
            int yi = points[i][1];
            for (int j = i + 1; j < n; j++) {
                int xj = points[j][0];
                int yj = points[j][1];
                int sx = xi + xj;
                int sy = yi + yj;
                long d2 =
                        (long) (xi - xj) * (xi - xj) + (long) (yi - yj) * (yi - yj);
                String key = sx + "," + sy + "," + d2;
                groups.computeIfAbsent(key, k -> new ArrayList<>()).add(new int[] {i, j});
            }
        }

        double best = Double.POSITIVE_INFINITY;
        for (List<int[]> lst : groups.values()) {
            int m = lst.size();
            for (int a = 0; a < m; a++) {
                int[] ij = lst.get(a);
                int i = ij[0];
                int j = ij[1];
                int xi = points[i][0];
                int yi = points[i][1];
                int xj = points[j][0];
                int yj = points[j][1];
                for (int b = a + 1; b < m; b++) {
                    int[] kl = lst.get(b);
                    int k = kl[0];
                    int l = kl[1];
                    if (i == k || i == l || j == k || j == l) {
                        continue;
                    }
                    int xk = points[k][0];
                    int yk = points[k][1];
                    int xl = points[l][0];
                    int yl = points[l][1];
                    long cross =
                            (long) (xi - xj) * (yk - yl) - (long) (yi - yj) * (xk - xl);
                    double area = Math.abs(cross) / 2.0;
                    if (area < best) {
                        best = area;
                    }
                }
            }
        }

        return best == Double.POSITIVE_INFINITY ? 0.0 : best;
    }
}
// @lc code=end
