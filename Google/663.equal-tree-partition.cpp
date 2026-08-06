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
    vector<long long> sums;

    long long dfs(TreeNode* node) {
        if (!node) return 0;
        long long total = node->val + dfs(node->left) + dfs(node->right);
        sums.push_back(total);
        return total;
    }

public:
    bool checkEqualTree(TreeNode* root) {
        sums.clear();
        long long total = dfs(root);
        sums.pop_back();
        if (total % 2) return false;
        return find(sums.begin(), sums.end(), total / 2) != sums.end();
    }
};

/*
Interview explanation:
Cutting one edge separates a child subtree. Equal partition exists exactly when some non-root subtree sum equals total/2.

C++ data structures: vector<long long> stores subtree sums; long long is safer for accumulated sums.

Edge cases: remove the root sum because cutting above the root is invalid; total zero still requires another zero subtree.

Complexity: O(n) time and O(n) space.
*/
