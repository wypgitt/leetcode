// Translated from 919.complete-binary-tree-inserter.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=919 lang=python3
// #
// # [919] Complete Binary Tree Inserter
// #
// 
// # =============================================================================
// # INTERVIEW: PROBLEM & INTERFACE
// # =============================================================================
// #
// # You have a complete binary tree (CBT): every level is full except possibly the
// # last level, and nodes on the last level are packed from left to right (no gaps).
// #
// # Design a class CBTInserter that supports:
// #   - __init__(root): store the initial tree.
// #   - insert(val): insert a new node with value val as the *next* node in CBT order
// #     (the next free slot in level-order / left-to-right fill). Return the value
// #     of the **parent** of the inserted node (problem requirement).
// #   - get_root(): return the current root.
// #
// # Constraints guarantee up to 1000 inserts per test and tree size such that this
// # design is practical with O(n) init and O(1) per insert.
// #
// # =============================================================================
// # KEY OBSERVATION — WHERE DOES THE NEXT NODE GO?
// # =============================================================================
// #
// # In a complete binary tree, the **next** insertion position is unique:
// #   - Do a level-order (BFS) walk.
// #   - The **first** node that does not yet have **two** children is the parent
// #     for the next insert.
// #   - If that parent has no left child, attach the new node as **left**;
// #     otherwise attach as **right**, and that parent is now **full** (both slots
// #     used) and will never receive another child.
// #
// # So we need a structure that:
// #   (1) Tells us the “current parent” in O(1) amortized time per insert.
// #   (2) After each insert, updates which node is next — without scanning the
// #       whole tree every time.
// #
// # =============================================================================
// # WHY A QUEUE (BFS FRONTIER OF “INCOMPLETE” NODES)
// # =============================================================================
// #
// # Maintain a queue `candidate_q` of TreeNodes that still need at least one child,
// # **in BFS order** (same order as if we listed all nodes level by level, left
// # to right, and kept only those missing a left or right).
// #
// # Invariant:
// #   - The **front** of the queue is always the parent for the **next** insert.
// #   - Nodes appear in queue in the order their empty child slots will be filled
// #     (complete-tree property).
// #
// # Initialization:
// #   - Run one BFS from `root`. For every visited node, if it lacks a left or a
// #     right child, append it to `candidate_q`. Continue the full BFS so we catch
// #     all “open” nodes in correct order (only nodes on the last incomplete level
// #     and possibly one node above actually appear, but the generic BFS rule is
// #     correct and simple to code).
// #
// # insert(val):
// #   - Let `parent = candidate_q[0]`.
// #   - Create `child = TreeNode(val)`.
// #   - If `parent.left is None`: set `parent.left = child`.
// #   - Else: `parent.right = child`, then **pop** `parent` from the queue because
// #     both children are now present.
// #   - Always **append** `child` to `candidate_q`: the new leaf may receive future
// #     children when the tree grows.
// #   - Return `parent.val`.
// #
// # Why append the new node every time?
// #   Every inserted node becomes a leaf and will eventually be the parent of later
// #   nodes once nodes to its left (in level order) are saturated — exactly how a
// #   complete tree expands.
// #
// # =============================================================================
// # WHY NOT OTHER APPROACHES?
// # =============================================================================
// #
// # - **Rescan full tree each insert (BFS from root)** — Correct but O(size) per
// #   insert → too slow if many inserts.
// #
// # - **Heap-style array index** — If the tree were stored as array `A` where
// #   node `i` has children `2i+1`, `2i+2`, you could track the next index `k` for
// #   insertion and parent `(k-1)//2`. That is O(1) and O(1) extra space **if** you
// #   only kept an array. Here the API is **linked TreeNodes**, so you still need
// #   either to rebuild pointers from indices or maintain the queue — the queue
// #   matches the linked representation cleanly without index math on every step.
// #
// # - **DFS** — Does not naturally yield “next slot” in level order without extra
// #   state; BFS / queue is the idiomatic match.
// #
// # =============================================================================
// # CORRECTNESS SKETCH
// # =============================================================================
// #
// # Base: After init, `candidate_q` lists every node with fewer than two children,
// # in level-order. The first such node in a complete tree is exactly where the
// # next node belongs (definition of level-order fill).
// #
// # Step: Suppose invariant holds before an insert. We attach to `parent = front`
// # per the rule (left if empty, else right). If we filled the second slot, remove
// # `parent`; the next front is the next node in level-order still missing a child.
// # We enqueue the new leaf; it is the last “open” node in order until earlier
// # nodes receive their children. By induction the invariant holds.
// #
// # =============================================================================
// # TIME & SPACE COMPLEXITY
// # =============================================================================
// #
// # __init__(root):
// #   - One BFS over the tree: **O(N)** time for N nodes initially.
// #   - Queue stores at most O(N) nodes in worst case (e.g. last level mostly open);
// #     typical complete tree: **O(width)** ~ **O(N)** worst-case auxiliary for the
// #     candidate queue plus BFS frontier — **O(N)** space.
// #
// # insert(val):
// #   - O(1): constant-time pointer assignments, deque popleft/append from ends.
// #
// # get_root():
// #   - O(1).
// #
// # Across **M** inserts after init: **O(M)** total time for inserts, **O(N+M)**
// # nodes in tree; queue size stays O(number of leaves / incomplete nodes on the
// # frontier) — **O(N+M)** worst-case bound for auxiliary storage tied to tree size.
// #
// # =============================================================================
// # EDGE CASES & TESTS
// # =============================================================================
// #
// # - **Single-node tree** — Queue init: root has no children → [root]. First
// #   insert attaches left child; return root.val.
// # - **Insert until root gets both children** — Second insert fills right;
// #   root leaves queue; returns root.val again for that insert’s parent.
// # - **Many inserts** — Queue never empties before tree grows (each new leaf is
// #   enqueued); parent always exists while inserts allowed by problem.
// #
// # Mental check: Tree [1], insert 2 → parent 1; insert 3 → parent 1; insert 4 →
// # parent 2 (level order: 2’s left). Matches manual CBT construction.
// #
// # =============================================================================
// # IMPROVEMENTS / VARIANTS
// # =============================================================================
// #
// # - If the judge allowed **only array storage**, use index arithmetic for true
// #   O(1) space beyond the array — not applicable when returning actual TreeNode
// #   graph.
// # - **Deque** from collections for O(1) pops from front; list.pop(0) would be O(n).
// #
// # =============================================================================
// 
// # @lc code=start
// from collections import deque
// from typing import Deque, Optional
// 
// 
// # Definition for a binary tree node (provided by LeetCode online judge).
// # class TreeNode:
// #     def __init__(self, val=0, left=None, right=None):
// #         self.val = val
// #         self.left = left
// #         self.right = right
// 
// 
// class CBTInserter:
//     """
//     Maintains a queue of nodes that still need one or two children (BFS order).
//     The front of the queue is always the parent for the next insert.
//     """
// 
//     def __init__(self, root: Optional["TreeNode"]):
//         self.root = root
//         # Nodes that do not yet have two children; next parent is at index 0.
//         self._candidates: Deque["TreeNode"] = deque()
// 
//         if root is None:
//             return
// 
//         bfs = deque([root])
//         while bfs:
//             node = bfs.popleft()
//             if node.left is None or node.right is None:
//                 self._candidates.append(node)
//             if node.left is not None:
//                 bfs.append(node.left)
//             if node.right is not None:
//                 bfs.append(node.right)
// 
//     def insert(self, val: int) -> int:
//         parent = self._candidates[0]
//         child = TreeNode(val)
// 
//         if parent.left is None:
//             parent.left = child
//         else:
//             parent.right = child
//             self._candidates.popleft()
// 
//         self._candidates.append(child)
//         return parent.val
// 
//     def get_root(self) -> Optional["TreeNode"]:
//         return self.root
// 
// 
// # Your CBTInserter object will be instantiated and called as such:
// # obj = CBTInserter(root)
// # param_1 = obj.insert(val)
// # param_2 = obj.get_root()
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

class CBTInserter {
    TreeNode* root;
    deque<TreeNode*> candidates;

public:
    CBTInserter(TreeNode* root) : root(root) {
        if (!root) return;
        queue<TreeNode*> q;
        q.push(root);
        while (!q.empty()) {
            TreeNode* node = q.front();
            q.pop();
            if (!node->left || !node->right) candidates.push_back(node);
            if (node->left) q.push(node->left);
            if (node->right) q.push(node->right);
        }
    }

    int insert(int val) {
        TreeNode* parent = candidates.front();
        TreeNode* child = new TreeNode(val);
        if (!parent->left) parent->left = child;
        else {
            parent->right = child;
            candidates.pop_front();
        }
        candidates.push_back(child);
        return parent->val;
    }

    TreeNode* get_root() { return root; }
};
