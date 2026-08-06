/*
 * @lc app=leetcode id=1172 lang=java
 *
 * [1172] Dinner Plate Stacks
 */

/*
 * --- Interview notes (operations, heaps, lazy deletion, trim, complexity, edges, alternatives) ---
 *
 * Problem
 * Infinitely many stacks in a row, indexed 0, 1, 2, … Each stack holds at most `capacity` plates.
 * • push(val) — push onto the **leftmost** stack that still has room (length < capacity). If none exist, open a **new**
 *   stack at the **right** end and push there.
 * • pop() — pop from the **rightmost** stack that is **non-empty**. Return -1 if everything empty.
 * • popAtStack(index) — pop top of stack `index`; return -1 if that stack missing or empty.
 *
 * Why naive scanning is too slow
 * `push` wants min index with space; `pop` wants max index with content. Repeated linear scans over all stacks can be
 * O(number of stacks) per call — too slow under ~2·10⁵ operations if stacks grow large.
 *
 * Data structures
 * 1. **`stacks: List<List<int>>`** — dynamic array of stacks (list as stack: append / pop from end).
 * 2. **`avail` — min-heap** of indices `i` such that we *believe* `len(stacks[i]) < capacity`. Supports “leftmost stack
 *    with room”: smallest valid index is heap minimum.
 * 3. **`nonempty` — max-heap`** — Java `PriorityQueue` with reverse order so peek is largest index.
 *    Gives “rightmost non-empty stack” among recorded candidates.
 *
 * Lazy deletion (stale heap entries)
 * After pops, some heap entries point to stacks that are now full (`avail`) or empty (`nonempty`). Instead of eagerly
 * removing them (expensive), **peek/pop from the heap until the top refers to a currently valid index** (still has room /
 * still non-empty). Amortized cost stays logarithmic per operation over the sequence.
 *
 * Trailing empty stacks
 * After `pop()` or `popAtStack`, repeatedly drop **only** `stacks[-1]` while it is empty. This keeps the array from growing
 * forever with useless trailing shells and keeps “new stack” creation aligned with need. Inner holes (empty stacks before
 * the last index) are **kept** — their indices stay valid and remain in `avail` for future `push`.
 *
 * Algorithm walkthrough
 * • **push(val)** — Pop stale tops from `avail`. If empty, append `[]`, push its index onto `avail`. Pop smallest usable
 *   index `idx`, append `val`, push `idx` onto `nonempty`. If stack still has room, push `idx` back onto `avail`.
 * • **pop()** — Pop stale tops from `nonempty`. Pop largest valid index `i`, pop plate from `stacks[i]`. If stack now has
 *   room, push `i` on `avail`; if still non-empty, push `i` on `nonempty`. Trim trailing empty stacks.
 * • **popAtStack(index)** — Bounds / empty check; pop top; push `index` onto `avail` (slot freed); trim trailing empties.
 *
 * Time complexity (typical analysis)
 * Each operation: O(log K) heap work where K is heap size (bounded by number of operations), plus amortized O(1) trim at
 * stack end. Overall **O(log N)** per call with N ~ stack count / operations.
 *
 * Space complexity
 * **O(S)** for stored plates plus **O(H)** for heaps — **O(S + Q)** over Q operations in worst case for heap garbage (still
 * acceptable on LC constraints).
 *
 * Edge cases
 * • capacity = 1 — each stack holds one plate; `avail` always tracks singleton holes after pops.
 * • pop / popAtStack on empty → -1.
 * • Large `index` with sparse stacks — list length check prevents out-of-range.
 *
 * Tests (statement Example 1)
 * capacity 2, sequence push 1..5, popAtStack(0), push 20,21, popAtStack(0), popAtStack(2), then pops → outputs
 * 2,20,21,5,4,3,1,-1 as in problem.
 *
 * Alternatives / improvements
 * • **Sorted containers** (TreeSet of indices) — same logarithmic bounds, clearer “valid set” semantics.
 * • **Explicit doubly-linked list** of non-empty / non-full stacks — O(1) updates if carefully maintained; more code.
 * • **Periodic heap rebuild** if memory of stale entries becomes an issue (rare in contests).
 *
 * --- end notes ---
 */

// @lc code=start
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.PriorityQueue;

public class DinnerPlates {

    private final int c;
    private final List<List<Integer>> stacks;
    private final PriorityQueue<Integer> avail;
    private final PriorityQueue<Integer> nonempty;

    public DinnerPlates(int capacity) {
        this.c = capacity;
        this.stacks = new ArrayList<>();
        this.avail = new PriorityQueue<>();
        this.nonempty = new PriorityQueue<>(Collections.reverseOrder());
    }

    public void push(int val) {
        while (!avail.isEmpty()) {
            int idx = avail.peek();
            if (idx >= stacks.size() || stacks.get(idx).size() >= c) {
                avail.poll();
            } else {
                break;
            }
        }
        if (avail.isEmpty()) {
            stacks.add(new ArrayList<>());
            avail.add(stacks.size() - 1);
        }
        int idx = avail.poll();
        stacks.get(idx).add(val);
        nonempty.add(idx);
        if (stacks.get(idx).size() < c) {
            avail.add(idx);
        }
    }

    public int pop() {
        while (!nonempty.isEmpty()) {
            int i = nonempty.peek();
            if (i < stacks.size() && !stacks.get(i).isEmpty()) {
                break;
            }
            nonempty.poll();
        }
        if (nonempty.isEmpty()) {
            return -1;
        }
        int i = nonempty.poll();
        List<Integer> st = stacks.get(i);
        int val = st.remove(st.size() - 1);
        if (st.size() < c) {
            avail.add(i);
        }
        if (!st.isEmpty()) {
            nonempty.add(i);
        }
        while (stacks.size() > 1 && stacks.get(stacks.size() - 1).isEmpty()) {
            stacks.remove(stacks.size() - 1);
        }
        return val;
    }

    public int popAtStack(int index) {
        if (index >= stacks.size() || stacks.get(index).isEmpty()) {
            return -1;
        }
        List<Integer> st = stacks.get(index);
        int val = st.remove(st.size() - 1);
        avail.add(index);
        while (stacks.size() > 1 && stacks.get(stacks.size() - 1).isEmpty()) {
            stacks.remove(stacks.size() - 1);
        }
        return val;
    }
}

/*
Your DinnerPlates object will be instantiated and called as such:
DinnerPlates obj = new DinnerPlates(capacity);
obj.push(val);
int param_2 = obj.pop();
int param_3 = obj.popAtStack(index);
*/
// @lc code=end
