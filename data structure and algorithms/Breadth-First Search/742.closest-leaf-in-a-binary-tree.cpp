#include <algorithm>
#include <array>
#include <cmath>
#include <climits>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <random>
#include <regex>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode* left, TreeNode* right) : val(x), left(left), right(right) {}
};

class Solution {
    unordered_map<TreeNode*, vector<TreeNode*>> graph;
    TreeNode* target = nullptr;

    void build(TreeNode* node, TreeNode* parent, int k) {
        if (!node) return;
        if (node->val == k) target = node;
        if (parent) {
            graph[node].push_back(parent);
            graph[parent].push_back(node);
        }
        build(node->left, node, k);
        build(node->right, node, k);
    }

public:
    int findClosestLeaf(TreeNode* root, int k) {
        graph.clear();
        target = nullptr;
        build(root, nullptr, k);
        queue<TreeNode*> q;
        unordered_set<TreeNode*> seen;
        q.push(target);
        seen.insert(target);
        while (!q.empty()) {
            TreeNode* node = q.front(); q.pop();
            if (!node->left && !node->right) return node->val;
            for (TreeNode* nei : graph[node]) if (!seen.count(nei)) {
                seen.insert(nei);
                q.push(nei);
            }
        }
        return root->val;
    }
};

/*
Interview explanation:
The nearest leaf may be through an ancestor, so treat the tree as an undirected graph with parent links and BFS from the target node.

C++ data structures: unordered_map<TreeNode*, vector<TreeNode*>> stores adjacency by node pointer; unordered_set<TreeNode*> tracks visited nodes.

Edge cases: if k is already a leaf, BFS returns immediately.

Complexity: O(n) time and O(n) space.
*/
