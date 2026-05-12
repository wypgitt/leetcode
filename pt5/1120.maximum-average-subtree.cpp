#include <algorithm>
#include <array>
#include <climits>
#include <cmath>
#include <condition_variable>
#include <cstdlib>
#include <deque>
#include <functional>
#include <map>
#include <mutex>
#include <numeric>
#include <queue>
#include <set>
#include <sstream>
#include <stack>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

// LeetCode provides TreeNode.
// struct TreeNode { int val; TreeNode *left; TreeNode *right; };

class Solution {
public:
    double maximumAverageSubtree(TreeNode* root) {
        best = 0.0;
        dfs(root);
        return best;
    }

private:
    double best = 0.0;

    pair<int, int> dfs(TreeNode* node) {
        if (!node) return {0, 0};
        auto [leftSum, leftCount] = dfs(node->left);
        auto [rightSum, rightCount] = dfs(node->right);

        int sum = leftSum + rightSum + node->val;
        int count = leftCount + rightCount + 1;
        best = max(best, static_cast<double>(sum) / count);
        return {sum, count};
    }
};

/*
Interview Explanation

Core idea:
The average of a subtree needs its sum and node count. Postorder DFS computes
those values bottom-up for every subtree.

C++ data structures:
- pair<int,int> returns {sum, count}.
- A double field stores the best average seen.

Algorithm:
1. Recurse into left and right children.
2. Combine their sums/counts with the current node.
3. Update best with sum / count.
4. Return this subtree's sum and count to the parent.

Correctness:
Every subtree is rooted at some node. Postorder DFS computes the exact sum and
count for each node's subtree after processing its children, so every subtree
average is considered and the maximum is returned.

Complexity:
O(n) time and O(h) recursion space.

Edge cases:
- Single node average is its value.
- Leaf subtrees are considered.
*/
