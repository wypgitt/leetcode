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
    int height(TreeNode* node) {
        if (!node) return 0;
        return 1 + max(height(node->left), height(node->right));
    }

    void place(TreeNode* node, int r, int lo, int hi, vector<vector<string>>& ans) {
        if (!node) return;
        int mid = (lo + hi) / 2;
        ans[r][mid] = to_string(node->val);
        place(node->left, r + 1, lo, mid - 1, ans);
        place(node->right, r + 1, mid + 1, hi, ans);
    }

public:
    vector<vector<string>> printTree(TreeNode* root) {
        int h = height(root), cols = (1 << h) - 1;
        vector<vector<string>> ans(h, vector<string>(cols, ""));
        place(root, 0, 0, cols - 1, ans);
        return ans;
    }
};

/*
Interview explanation:
A tree of height h uses h rows and 2^h-1 columns. Place each node at the midpoint of its assigned range; children receive left and right halves.

C++ data structures: vector<vector<string>> is the required output matrix.

Edge cases: null children leave empty strings.

Complexity: O(n + h*2^h) time due to grid initialization and node placement; output space O(h*2^h).
*/
