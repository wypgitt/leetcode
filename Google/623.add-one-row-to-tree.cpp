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
public:
    TreeNode* addOneRow(TreeNode* root, int val, int depth) {
        if (depth == 1) return new TreeNode(val, root, nullptr);
        queue<TreeNode*> q;
        q.push(root);
        for (int d = 1; d < depth - 1; ++d) {
            int sz = q.size();
            while (sz--) {
                TreeNode* node = q.front(); q.pop();
                if (node->left) q.push(node->left);
                if (node->right) q.push(node->right);
            }
        }
        while (!q.empty()) {
            TreeNode* node = q.front(); q.pop();
            TreeNode* oldLeft = node->left;
            TreeNode* oldRight = node->right;
            node->left = new TreeNode(val, oldLeft, nullptr);
            node->right = new TreeNode(val, nullptr, oldRight);
        }
        return root;
    }
};

/*
Interview explanation:
Only nodes at depth-1 are modified. BFS reaches that level, then inserts new children while preserving old subtrees under the proper side.

C++ data structures: queue<TreeNode*> performs level-order traversal; new allocates inserted nodes as LeetCode expects.

Edge cases: depth=1 creates a new root.

Complexity: O(n) time worst case and O(w) queue space for the widest level.
*/
