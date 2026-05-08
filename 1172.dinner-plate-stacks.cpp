// Translated from 1172.dinner-plate-stacks.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=1172 lang=python3
// #
// # [1172] Dinner Plate Stacks
// #
// 
// # --- Interview notes (operations, heaps, lazy deletion, trim, complexity, edges, alternatives) ---
// #
// # Problem
// # Infinitely many stacks in a row, indexed 0, 1, 2, … Each stack holds at most `capacity` plates.
// # • push(val) — push onto the **leftmost** stack that still has room (length < capacity). If none exist, open a **new**
// #   stack at the **right** end and push there.
// # • pop() — pop from the **rightmost** stack that is **non-empty**. Return -1 if everything empty.
// # • popAtStack(index) — pop top of stack `index`; return -1 if that stack missing or empty.
// #
// # Why naive scanning is too slow
// # `push` wants min index with space; `pop` wants max index with content. Repeated linear scans over all stacks can be
// # O(number of stacks) per call — too slow under ~2·10⁵ operations if stacks grow large.
// #
// # Data structures
// # 1. **`stacks: List[List[int]]`** — dynamic array of stacks (Python list as stack: append / pop from end).
// # 2. **`avail` — min-heap** of indices `i` such that we *believe* `len(stacks[i]) < capacity`. Supports “leftmost stack
// #    with room”: smallest valid index is heap minimum.
// # 3. **`nonempty` — max-heap via negatives** — store `-i` in a min-heap so smallest `-i` corresponds to largest `i`.
// #    Gives “rightmost non-empty stack” among recorded candidates.
// #
// # Lazy deletion (stale heap entries)
// # After pops, some heap entries point to stacks that are now full (`avail`) or empty (`nonempty`). Instead of eagerly
// # removing them (expensive), **peek/pop from the heap until the top refers to a currently valid index** (still has room /
// # still non-empty). Amortized cost stays logarithmic per operation over the sequence.
// #
// # Trailing empty stacks
// # After `pop()` or `popAtStack`, repeatedly drop **only** `stacks[-1]` while it is empty. This keeps the array from growing
// # forever with useless trailing shells and keeps “new stack” creation aligned with need. Inner holes (empty stacks before
// # the last index) are **kept** — their indices stay valid and remain in `avail` for future `push`.
// #
// # Algorithm walkthrough
// # • **push(val)** — Pop stale tops from `avail`. If empty, append `[]`, push its index onto `avail`. Pop smallest usable
// #   index `idx`, append `val`, push `-idx` onto `nonempty`. If stack still has room, push `idx` back onto `avail`.
// # • **pop()** — Pop stale tops from `nonempty`. Pop largest valid index `i`, pop plate from `stacks[i]`. If stack now has
// #   room, push `i` on `avail`; if still non-empty, push `-i` on `nonempty`. Trim trailing empty stacks.
// # • **popAtStack(index)** — Bounds / empty check; pop top; push `index` onto `avail` (slot freed); trim trailing empties.
// #
// # Time complexity (typical analysis)
// # Each operation: O(log K) heap work where K is heap size (bounded by number of operations), plus amortized O(1) trim at
// # stack end. Overall **O(log N)** per call with N ~ stack count / operations.
// #
// # Space complexity
// # **O(S)** for stored plates plus **O(H)** for heaps — **O(S + Q)** over Q operations in worst case for heap garbage (still
// # acceptable on LC constraints).
// #
// # Edge cases
// # • capacity = 1 — each stack holds one plate; `avail` always tracks singleton holes after pops.
// # • pop / popAtStack on empty → -1.
// # • Large `index` with sparse stacks — list length check prevents out-of-range.
// #
// # Tests (statement Example 1)
// # capacity 2, sequence push 1..5, popAtStack(0), push 20,21, popAtStack(0), popAtStack(2), then pops → outputs
// # 2,20,21,5,4,3,1,-1 as in problem.
// #
// # Alternatives / improvements
// # • **Sorted containers** (TreeSet of indices) — same logarithmic bounds, clearer “valid set” semantics.
// # • **Explicit doubly-linked list** of non-empty / non-full stacks — O(1) updates if carefully maintained; more code.
// # • **Periodic heap rebuild** if memory of stale entries becomes an issue (rare in contests).
// #
// # --- end notes ---
// 
// # @lc code=start
// import heapq
// from typing import List
// 
// 
// class DinnerPlates:
//     def __init__(self, capacity: int):
//         self.c = capacity
//         self.stacks: List[List[int]] = []
//         self.avail = []
//         self.nonempty = []
// 
//     def push(self, val: int) -> None:
//         while self.avail and (
//             self.avail[0] >= len(self.stacks) or len(self.stacks[self.avail[0]]) >= self.c
//         ):
//             heapq.heappop(self.avail)
//         if not self.avail:
//             self.stacks.append([])
//             heapq.heappush(self.avail, len(self.stacks) - 1)
//         idx = heapq.heappop(self.avail)
//         self.stacks[idx].append(val)
//         heapq.heappush(self.nonempty, -idx)
//         if len(self.stacks[idx]) < self.c:
//             heapq.heappush(self.avail, idx)
// 
//     def pop(self) -> int:
//         while self.nonempty:
//             i = -self.nonempty[0]
//             if i < len(self.stacks) and self.stacks[i]:
//                 break
//             heapq.heappop(self.nonempty)
//         else:
//             return -1
//         i = -heapq.heappop(self.nonempty)
//         val = self.stacks[i].pop()
//         if len(self.stacks[i]) < self.c:
//             heapq.heappush(self.avail, i)
//         if self.stacks[i]:
//             heapq.heappush(self.nonempty, -i)
//         while len(self.stacks) > 1 and not self.stacks[-1]:
//             self.stacks.pop()
//         return val
// 
//     def popAtStack(self, index: int) -> int:
//         if index >= len(self.stacks) or not self.stacks[index]:
//             return -1
//         val = self.stacks[index].pop()
//         heapq.heappush(self.avail, index)
//         while len(self.stacks) > 1 and not self.stacks[-1]:
//             self.stacks.pop()
//         return val
// 
// 
// # Your DinnerPlates object will be instantiated and called as such:
// # obj = DinnerPlates(capacity)
// # obj.push(val)
// # param_2 = obj.pop()
// # param_3 = obj.popAtStack(index)
// # @lc code=end

#include <algorithm>
#include <array>
#include <cctype>
#include <climits>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <deque>
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

// C++ translation notes:
// - Python list/deque/heap/dict/set are translated to vector/deque/priority_queue/map or unordered_map/set.
// - TreeNode and ListNode are supplied by LeetCode. Define LOCAL_LEETCODE_STUBS for local-only compilation of tree/list solutions.
#ifdef LOCAL_LEETCODE_STUBS
struct ListNode {
    int val;
    ListNode* next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode* next) : val(x), next(next) {}
};
struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode* left, TreeNode* right) : val(x), left(left), right(right) {}
};
#endif

class DinnerPlates {
    int capacity;
    vector<vector<int>> stacks;
    priority_queue<int, vector<int>, greater<int>> avail;
    priority_queue<int> nonempty;

    void trim() {
        while (stacks.size() > 1 && stacks.back().empty()) stacks.pop_back();
    }

public:
    DinnerPlates(int capacity) : capacity(capacity) {}

    void push(int val) {
        while (!avail.empty() && (avail.top() >= (int)stacks.size() || (int)stacks[avail.top()].size() >= capacity)) avail.pop();
        if (avail.empty()) {
            stacks.push_back({});
            avail.push((int)stacks.size() - 1);
        }
        int idx = avail.top();
        avail.pop();
        stacks[idx].push_back(val);
        nonempty.push(idx);
        if ((int)stacks[idx].size() < capacity) avail.push(idx);
    }

    int pop() {
        while (!nonempty.empty()) {
            int i = nonempty.top();
            if (i < (int)stacks.size() && !stacks[i].empty()) break;
            nonempty.pop();
        }
        if (nonempty.empty()) return -1;
        int i = nonempty.top();
        nonempty.pop();
        int val = stacks[i].back();
        stacks[i].pop_back();
        if ((int)stacks[i].size() < capacity) avail.push(i);
        if (!stacks[i].empty()) nonempty.push(i);
        trim();
        return val;
    }

    int popAtStack(int index) {
        if (index >= (int)stacks.size() || stacks[index].empty()) return -1;
        int val = stacks[index].back();
        stacks[index].pop_back();
        avail.push(index);
        trim();
        return val;
    }
};
