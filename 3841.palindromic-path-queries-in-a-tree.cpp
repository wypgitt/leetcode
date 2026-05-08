// Translated from 3841.palindromic-path-queries-in-a-tree.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3841 lang=python3
// #
// # [3841] Palindromic Path Queries in a Tree
// #
// #
// # --- Interview Notes ---------------------------------------------------------
// #
// # Problem restatement
// # We are given a tree with n nodes. Each node has a lowercase English character.
// # There are two types of operations:
// #
// #   update u c:
// #     change node u's character to c
// #
// #   query u v:
// #     look at the characters on the unique path from u to v, inclusive, and ask
// #     whether those characters can be rearranged into a palindrome
// #
// # Return the answers for all query operations.
// #
// #
// # Palindrome condition
// # A multiset of characters can be rearranged into a palindrome iff at most one
// # character has odd frequency.
// #
// # Examples:
// #   "aac" -> counts: a=2, c=1 -> one odd -> yes
// #   "abc" -> counts: a=1, b=1, c=1 -> three odds -> no
// #
// # We do not need exact counts. We only need each count's parity.
// #
// #
// # Bitmask representation
// # Use a 26-bit integer mask:
// #   bit 0 represents 'a'
// #   bit 1 represents 'b'
// #   ...
// #   bit 25 represents 'z'
// #
// # For one node with character c:
// #   mask = 1 << (ord(c) - ord('a'))
// #
// # XOR is perfect for parity:
// #   - seeing a character once toggles its bit on,
// #   - seeing it twice toggles the bit back off,
// #   - after XORing all node masks on a path, 1 bits are exactly the characters
// #     with odd frequency.
// #
// # Therefore:
// #   path can form a palindrome iff path_mask has at most one set bit.
// #
// # The classic bit trick for "at most one set bit" is:
// #   mask == 0 or (mask & (mask - 1)) == 0
// #
// #
// # Remaining challenge: dynamic path XOR queries
// # The tree is static, but node values change. We need:
// #   point update: change one node's mask
// #   path query: XOR masks on the path u..v
// #
// # This is exactly what Heavy-Light Decomposition (HLD) is for.
// #
// #
// # Heavy-Light Decomposition overview
// # HLD decomposes the tree into O(n) chains. Any root-to-node path crosses only
// # O(log n) light edges, so any arbitrary path u..v can be broken into O(log n)
// # contiguous chain segments.
// #
// # We assign every node a position in a base array so that each chain is
// # contiguous in that array.
// #
// # Then:
// #   node update -> segment tree point update at pos[node]
// #   path XOR query -> XOR over O(log n) array intervals
// #
// #
// # Segment tree
// # We build an iterative segment tree over the HLD base array.
// #
// # Operations:
// #   update(index, value): O(log n)
// #   query(left, right): XOR over inclusive range [left, right], O(log n)
// #
// # Since XOR is associative and has identity 0, it is a natural segment-tree
// # operation.
// #
// #
// # Algorithm steps
// #
// # 1. Build adjacency list from edges.
// # 2. Root the tree at node 0.
// # 3. First DFS pass:
// #      compute parent, depth, subtree size, and each node's heavy child.
// #      The heavy child is the child with the largest subtree.
// #
// # 4. Second HLD pass:
// #      assign each node:
// #        head[node] = top node of its heavy chain
// #        pos[node]  = index in the base array
// #      Heavy chains are written contiguously.
// #
// # 5. Build the segment tree from current character masks in HLD order.
// #
// # 6. For each operation:
// #      update u c:
// #        change chars[u]
// #        segment_tree.update(pos[u], mask(c))
// #
// #      query u v:
// #        compute path XOR with HLD
// #        answer true iff mask has at most one set bit
// #
// #
// # Why iterative DFS?
// # n can be 5 * 10^4. Python recursion can hit recursion-depth limits on a long
// # chain-shaped tree. The implementation uses iterative traversals to be robust.
// #
// #
// # Data structures and why we choose them
// #
// # 1. adjacency list
// #    Standard compact representation for a sparse tree. There are n - 1 edges.
// #
// # 2. arrays parent, depth, size, heavy
// #    HLD metadata. Arrays are faster and simpler than dictionaries because nodes
// #    are labeled 0..n-1.
// #
// # 3. arrays head and pos
// #    Convert tree paths into array intervals.
// #
// # 4. iterative segment tree
// #    Supports dynamic point updates and range XOR queries in O(log n).
// #
// # 5. 26-bit integer masks
// #    Compact parity representation. Query result is one integer, not a 26-entry
// #    frequency array.
// #
// #
// # Correctness proof
// #
// # Lemma 1: The XOR of node masks on a path has a set bit exactly for characters
// # with odd frequency on that path.
// # Proof:
// # A character's bit is toggled once per occurrence on the path. An even number of
// # toggles returns it to 0; an odd number leaves it as 1.
// #
// # Lemma 2: A path's characters can be rearranged into a palindrome iff its path
// # XOR mask has at most one set bit.
// # Proof:
// # A palindrome can have at most one character with odd count: the center
// # character in an odd-length palindrome. Conversely, if at most one character has
// # odd count, place half of every even pair on each side and optionally put the
// # odd character in the center. By Lemma 1, odd-count characters are exactly the
// # set bits of the mask.
// #
// # Lemma 3: HLD path decomposition covers exactly the nodes on path u..v.
// # Proof:
// # While u and v are on different heavy-chain heads, the deeper head's chain
// # segment from head to current node lies entirely on the u..v path. Removing that
// # segment moves that endpoint to the parent of the head. Repeating eventually
// # puts both endpoints on one chain, where the remaining path is the contiguous
// # segment between their positions. These segments are disjoint and together
// # cover exactly the original path.
// #
// # Lemma 4: The segment tree returns the XOR of current node masks for any HLD
// # array interval.
// # Proof:
// # The segment tree is built with each leaf equal to the current mask of the node
// # at that HLD position. Point updates replace exactly one leaf after character
// # changes. Since every internal node stores XOR of its children, a range query
// # returns the XOR of all leaves in that interval.
// #
// # Theorem: For every query u v, the algorithm returns true exactly when the path
// # characters can be rearranged into a palindrome.
// # Proof:
// # By Lemma 3, HLD decomposes path u..v into exact array intervals. By Lemma 4,
// # XORing segment-tree results for those intervals gives the XOR of all current
// # masks on the path. By Lemma 2, checking whether that mask has at most one set
// # bit is exactly the palindrome-rearrangement condition.
// #
// #
// # Complexity analysis
// #
// # Let n be the number of nodes and q be the number of operations.
// #
// # Preprocessing:
// #   - building adjacency: O(n)
// #   - HLD metadata and positions: O(n)
// #   - segment tree build: O(n)
// #
// # Each update:
// #   - one point update in the segment tree: O(log n)
// #
// # Each query:
// #   - HLD splits the path into O(log n) chain segments
// #   - each segment tree range query costs O(log n)
// #   - total O(log^2 n)
// #
// # Space:
// #   - adjacency and HLD arrays: O(n)
// #   - segment tree: O(n)
// #   Overall space complexity: O(n).
// #
// #
// # Tests to discuss in an interview
// #
// # 1. Example 1:
// #      n = 3, edges = [[0,1],[1,2]], s = "aac"
// #      ["query 0 2", "update 1 b", "query 0 2"] -> [true, false]
// #
// # 2. Example 2:
// #      Star tree with updates at root and leaf. Verifies paths through LCA/root.
// #
// # 3. Single node:
// #      Any query 0 0 is true, and updates should keep it true.
// #
// # 4. Long chain:
// #      Verifies iterative DFS avoids recursion limits and path decomposition
// #      works when the whole tree is one heavy chain.
// #
// # 5. Repeated updates on same node:
// #      Ensures segment tree point updates replace old values, not add to them.
// #
// # 6. Random brute force:
// #      For small n, compare this solution against a BFS parent-path finder and
// #      direct character counting after random updates.
// #
// #
// # Edge cases
// #
// # - u == v: one character always forms a palindrome.
// # - all characters same: every query is true.
// # - updates that keep the same character: harmless point replacement.
// # - tree can be a chain of length 5 * 10^4: use iterative traversals.
// #
// #
// # Possible improvements
// #
// # - Binary lifting with Euler-tour subtree range updates is not enough here
// #   because point updates on arbitrary nodes affect many root-to-node prefix
// #   masks dynamically.
// # - Link-cut trees would also support dynamic path XOR, but the tree topology is
// #   static, so HLD is simpler and more interview-friendly.
// # - If the operation count were much smaller, a brute-force path walk might pass
// #   some cases, but worst-case chains make it O(nq), too slow.
// #
// # -------------------------------------------------------------------------------
// 
// # @lc code=start
// from typing import List
// 
// 
// class SegmentTreeXor:
//     def __init__(self, values: List[int]) -> None:
//         size = 1
//         while size < len(values):
//             size <<= 1
//         self.size = size
//         self.tree = [0] * (2 * size)
// 
//         for i, value in enumerate(values):
//             self.tree[size + i] = value
//         for i in range(size - 1, 0, -1):
//             self.tree[i] = self.tree[2 * i] ^ self.tree[2 * i + 1]
// 
//     def update(self, index: int, value: int) -> None:
//         index += self.size
//         self.tree[index] = value
//         index //= 2
//         while index:
//             self.tree[index] = self.tree[2 * index] ^ self.tree[2 * index + 1]
//             index //= 2
// 
//     def query(self, left: int, right: int) -> int:
//         left += self.size
//         right += self.size
//         ans = 0
// 
//         while left <= right:
//             if left & 1:
//                 ans ^= self.tree[left]
//                 left += 1
//             if not (right & 1):
//                 ans ^= self.tree[right]
//                 right -= 1
//             left //= 2
//             right //= 2
// 
//         return ans
// 
// 
// class Solution:
//     def palindromePath(
//         self, n: int, edges: List[List[int]], s: str, queries: List[str]
//     ) -> List[bool]:
//         graph = [[] for _ in range(n)]
//         for u, v in edges:
//             graph[u].append(v)
//             graph[v].append(u)
// 
//         parent = [-1] * n
//         depth = [0] * n
//         order = [0]
// 
//         for node in order:
//             for nei in graph[node]:
//                 if nei == parent[node]:
//                     continue
//                 parent[nei] = node
//                 depth[nei] = depth[node] + 1
//                 order.append(nei)
// 
//         size = [1] * n
//         heavy = [-1] * n
//         for node in reversed(order):
//             best_size = 0
//             for nei in graph[node]:
//                 if parent[nei] == node:
//                     size[node] += size[nei]
//                     if size[nei] > best_size:
//                         best_size = size[nei]
//                         heavy[node] = nei
// 
//         head = [0] * n
//         pos = [0] * n
//         base = [0] * n
//         current_pos = 0
//         stack = [(0, 0)]
// 
//         while stack:
//             start, chain_head = stack.pop()
//             node = start
//             while node != -1:
//                 head[node] = chain_head
//                 pos[node] = current_pos
//                 base[current_pos] = self._mask(s[node])
//                 current_pos += 1
// 
//                 for nei in graph[node]:
//                     if parent[nei] == node and nei != heavy[node]:
//                         stack.append((nei, nei))
// 
//                 node = heavy[node]
// 
//         seg = SegmentTreeXor(base)
//         chars = list(s)
//         answer = []
// 
//         for raw in queries:
//             parts = raw.split()
//             if parts[0] == "update":
//                 node = int(parts[1])
//                 chars[node] = parts[2]
//                 seg.update(pos[node], self._mask(parts[2]))
//             else:
//                 u = int(parts[1])
//                 v = int(parts[2])
//                 mask = self._path_xor(u, v, head, parent, depth, pos, seg)
//                 answer.append(mask & (mask - 1) == 0)
// 
//         return answer
// 
//     def _path_xor(
//         self,
//         u: int,
//         v: int,
//         head: List[int],
//         parent: List[int],
//         depth: List[int],
//         pos: List[int],
//         seg: SegmentTreeXor,
//     ) -> int:
//         ans = 0
// 
//         while head[u] != head[v]:
//             if depth[head[u]] < depth[head[v]]:
//                 u, v = v, u
//             ans ^= seg.query(pos[head[u]], pos[u])
//             u = parent[head[u]]
// 
//         if depth[u] > depth[v]:
//             u, v = v, u
//         ans ^= seg.query(pos[u], pos[v])
//         return ans
// 
//     def _mask(self, ch: str) -> int:
//         return 1 << (ord(ch) - ord("a"))
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

class SegmentTreeXor {
    int size;
    vector<int> tree;
public:
    SegmentTreeXor(vector<int>& values) : size(1) {
        while (size < (int)values.size()) size <<= 1;
        tree.assign(2 * size, 0);
        for (int i = 0; i < (int)values.size(); ++i) tree[size + i] = values[i];
        for (int i = size - 1; i > 0; --i) tree[i] = tree[i << 1] ^ tree[i << 1 | 1];
    }
    void update(int idx, int val) {
        idx += size;
        tree[idx] = val;
        for (idx >>= 1; idx; idx >>= 1) tree[idx] = tree[idx << 1] ^ tree[idx << 1 | 1];
    }
    int query(int l, int r) {
        l += size;
        r += size;
        int ans = 0;
        while (l <= r) {
            if (l & 1) ans ^= tree[l++];
            if (!(r & 1)) ans ^= tree[r--];
            l >>= 1;
            r >>= 1;
        }
        return ans;
    }
};

class Solution {
    int mask(char ch) { return 1 << (ch - 'a'); }

    int pathXor(int u, int v, vector<int>& head, vector<int>& parent, vector<int>& depth, vector<int>& pos, SegmentTreeXor& seg) {
        int ans = 0;
        while (head[u] != head[v]) {
            if (depth[head[u]] < depth[head[v]]) swap(u, v);
            ans ^= seg.query(pos[head[u]], pos[u]);
            u = parent[head[u]];
        }
        if (depth[u] > depth[v]) swap(u, v);
        ans ^= seg.query(pos[u], pos[v]);
        return ans;
    }

public:
    vector<bool> palindromePath(int n, vector<vector<int>>& edges, string s, vector<string>& queries) {
        vector<vector<int>> graph(n);
        for (auto& e : edges) {
            graph[e[0]].push_back(e[1]);
            graph[e[1]].push_back(e[0]);
        }
        vector<int> parent(n, -1), depth(n), order{0};
        for (int node : order) for (int nei : graph[node]) if (nei != parent[node]) {
            parent[nei] = node;
            depth[nei] = depth[node] + 1;
            order.push_back(nei);
        }
        vector<int> size(n, 1), heavy(n, -1);
        for (int idx = n - 1; idx >= 0; --idx) {
            int node = order[idx], best = 0;
            for (int nei : graph[node]) if (parent[nei] == node) {
                size[node] += size[nei];
                if (size[nei] > best) best = size[nei], heavy[node] = nei;
            }
        }
        vector<int> head(n), pos(n), base(n);
        int cur = 0;
        vector<pair<int, int>> stack{{0, 0}};
        while (!stack.empty()) {
            auto [start, chainHead] = stack.back();
            stack.pop_back();
            for (int node = start; node != -1; node = heavy[node]) {
                head[node] = chainHead;
                pos[node] = cur;
                base[cur++] = mask(s[node]);
                for (int nei : graph[node]) if (parent[nei] == node && nei != heavy[node]) stack.push_back({nei, nei});
            }
        }
        SegmentTreeXor seg(base);
        vector<bool> ans;
        for (string raw : queries) {
            stringstream ss(raw);
            string op;
            ss >> op;
            if (op == "update") {
                int node;
                char ch;
                ss >> node >> ch;
                seg.update(pos[node], mask(ch));
            } else {
                int u, v;
                ss >> u >> v;
                int m = pathXor(u, v, head, parent, depth, pos, seg);
                ans.push_back((m & (m - 1)) == 0);
            }
        }
        return ans;
    }
};
