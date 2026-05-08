// Translated from 971.flip-binary-tree-to-match-preorder-traversal.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=971 lang=python3
// #
// # [971] Flip Binary Tree To Match Preorder Traversal
// #
// 
// # --- Interview notes (preorder simulation, greedy choice at each node, DFS, complexity) ---
// #
// # Problem
// # You are given the **`root`** of a binary tree and an array **`voyage`** — the **target preorder traversal** (values in the
// # order a preorder walk should visit nodes). You may **flip** any node any number of times: a **flip** swaps **`left`** and
// # **`right`** children (subtrees). Return the list of **values of nodes where you performed a flip**, in the order you flip.
// # If no sequence of flips can make the tree’s preorder equal **`voyage`**, return **`[-1]`**.
// #
// # Key observation — preorder structure
// # Preorder is **`root → preorder(left) → preorder(right)`**. After visiting **`root`**, the **next** value in preorder is:
// # • **Left child exists** (and we treat “promoted” side first): the **root value of the next subtree visited**.
// # • If **both** children exist **without** a flip at **`root`**, that next value **must** be **`left.val`** (start of left subtree’s
// #   preorder).
// # • If **both** children exist **with** a flip at **`root`**, children swap; preorder becomes **`root → preorder(right) →
// #   preorder(left)`**, so the next value **must** be **`right.val`**.
// #
// # Greedy choice (why it is correct)
// # At each node with **two** children, the **first** value after **`root`** in **`voyage`** uniquely tells us whether we need a
// # flip: match **`voyage[i]`** to **`left.val`** vs **`right.val`**. There is **no** lookahead trade-off — flipping later cannot
// # fix a wrong choice here because preorder **fixes** which subtree comes first **immediately** after **`root`**. So **one DFS**
// # that consumes **`voyage`** in lockstep is optimal and runs in **linear** time.
// #
// # Algorithm — DFS with index pointer
// # Maintain **`i`**, the index of the **next** expected preorder value.
// # **`dfs(node)`**:
// # 1. **Empty node** — return **`True`** (nothing to match).
// # 2. **`voyage[i] != node.val`** or **`i` out of range** — **fail**.
// # 3. **`i += 1`** (consume **`root`**).
// # 4. **Leaf** — **`True`**.
// # 5. **Only left child** — recurse **`left`** (next must start left subtree).
// # 6. **Only right child** — recurse **`right`**.
// # 7. **Both children** — if **`voyage[i] == left.val`**: recurse **`left`** then **`right`**. Else if **`voyage[i] ==
// #    right.val`**: **record `node.val`** in **`flips`**, recurse **`right`** then **`left`**. Else **fail**.
// # After DFS, success iff **`dfs(root)`** and **`i == len(voyage)`** (tree and array fully consumed together).
// #
// # Data structures
// # • **`voyage`** — input array (**O(n)`**).
// # • **`flips`** — list of flipped node values (**O(f) ⊆ O(n)`**).
// # • **Integer `i`** — cursor; **O(1)** extra space.
// # • **Recursion stack** — **O(h)`** height **`h`** (balanced **`O(log n)`**, skewed **`O(n)`**).
// #
// # Time complexity **O(n)`** — each node visited once; each **`voyage`** index advanced at most once per node visit.
// #
// # Space complexity **O(h)`** auxiliary for recursion (**output `flips` not counted** as extra problem space); **O(n)`** if output
// # lists all flips in worst case.
// #
// # Edge cases
// # • **`voyage`** length **≠** number of nodes — impossible (**`[-1]`**).
// # • **Single node** — **`voyage == [root.val]`**, **`[]`** flips.
// # • **Chain (one child each level)** — no flip decisions at two-child nodes; only value checks.
// # • **Both children, next value matches neither** — **`[-1]`** immediately at that node.
// #
// # Tests (mental / quick)
// # • Example shape: root **1**, children **2** and **3**; **`voyage = [1,3,2]`** → must flip at **1**, **`flips = [1]`**.
// # • **`voyage`** order **`[1,2,3]`** → no flip, **`flips = []`**.
// #
// # Improvements
// # • **Iterative DFS** with explicit stack + same logic removes recursion overhead (same asymptotics).
// # • **Early exit**: on first failure return **`[-1]`** without completing traversal (already implemented via boolean).
// #
// # --- end notes ---
// 
// # @lc code=start
// from typing import List, Optional
// 
// 
// # Definition for a binary tree node.
// # class TreeNode:
// #     def __init__(self, val=0, left=None, right=None):
// #         self.val = val
// #         self.left = left
// #         self.right = right
// class Solution:
//     def flipMatchVoyage(self, root: Optional[TreeNode], voyage: List[int]) -> List[int]:
//         i = 0
//         flips: List[int] = []
// 
//         def dfs(node: Optional[TreeNode]) -> bool:
//             nonlocal i
//             if not node:
//                 return True
//             if i >= len(voyage) or node.val != voyage[i]:
//                 return False
//             i += 1
// 
//             if not node.left and not node.right:
//                 return True
//             if node.left and not node.right:
//                 return dfs(node.left)
//             if node.right and not node.left:
//                 return dfs(node.right)
// 
//             if i >= len(voyage):
//                 return False
//             if voyage[i] == node.left.val:
//                 return dfs(node.left) and dfs(node.right)
//             if voyage[i] == node.right.val:
//                 flips.append(node.val)
//                 return dfs(node.right) and dfs(node.left)
//             return False
// 
//         if dfs(root) and i == len(voyage):
//             return flips
//         return [-1]
// 
// 
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

class Solution {
public:
    vector<int> flipMatchVoyage(TreeNode* root, vector<int>& voyage) {
        int i = 0;
        vector<int> flips;
        function<bool(TreeNode*)> dfs = [&](TreeNode* node) {
            if (!node) return true;
            if (i >= (int)voyage.size() || node->val != voyage[i]) return false;
            ++i;
            if (!node->left && !node->right) return true;
            if (node->left && !node->right) return dfs(node->left);
            if (node->right && !node->left) return dfs(node->right);
            if (i >= (int)voyage.size()) return false;
            if (voyage[i] == node->left->val) return dfs(node->left) && dfs(node->right);
            if (voyage[i] == node->right->val) {
                flips.push_back(node->val);
                return dfs(node->right) && dfs(node->left);
            }
            return false;
        };
        if (dfs(root) && i == (int)voyage.size()) return flips;
        return {-1};
    }
};
