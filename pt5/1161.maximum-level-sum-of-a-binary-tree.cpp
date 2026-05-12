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
    int maxLevelSum(TreeNode* root) {
        queue<TreeNode*> q;
        q.push(root);
        int level = 1;
        int bestLevel = 1;
        int bestSum = INT_MIN;

        while (!q.empty()) {
            int size = q.size();
            int sum = 0;
            while (size--) {
                TreeNode* node = q.front();
                q.pop();
                sum += node->val;
                if (node->left) q.push(node->left);
                if (node->right) q.push(node->right);
            }
            if (sum > bestSum) {
                bestSum = sum;
                bestLevel = level;
            }
            ++level;
        }

        return bestLevel;
    }
};

/*
Interview Explanation

Core idea:
Level order traversal naturally groups nodes by depth. Sum each level and keep
the first level with the largest sum.

C++ data structures:
- queue<TreeNode*> performs BFS.
- Integers track current level and best sum.

Algorithm:
1. Push root into the queue.
2. For each BFS layer, process exactly its current size.
3. Sum node values and enqueue children.
4. Update best only on strictly greater sum to preserve smallest level.

Correctness:
BFS processes nodes level by level. The computed sum for each layer is exact,
and comparing all levels finds the maximum. Strict comparison preserves the
earliest level in ties.

Complexity:
O(n) time and O(w) space, where w is maximum tree width.

Edge cases:
- Negative values require bestSum initialized to INT_MIN.
- Single node returns level 1.
*/
