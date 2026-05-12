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
    bool btreeGameWinningMove(TreeNode* root, int n, int x) {
        target = x;
        leftSize = rightSize = 0;
        count(root);
        int parentSide = n - leftSize - rightSize - 1;
        int biggest = max(parentSide, max(leftSize, rightSize));
        return biggest > n / 2;
    }

private:
    int target;
    int leftSize = 0;
    int rightSize = 0;

    int count(TreeNode* node) {
        if (!node) return 0;
        int left = count(node->left);
        int right = count(node->right);
        if (node->val == target) {
            leftSize = left;
            rightSize = right;
        }
        return left + right + 1;
    }
};

/*
Interview Explanation

Core idea:
After the first player colors node x, the second player can choose one of
three regions: x's left subtree, x's right subtree, or everything above x. The
second player wins if any region has more than half the nodes.

C++ data structures:
- DFS counts subtree sizes.
- Integer fields store the left and right subtree sizes of x.

Algorithm:
1. Count every subtree.
2. When node x is found, record sizes of its left and right subtrees.
3. Parent-side size is n - left - right - 1.
4. Return true if the largest region has more than n/2 nodes.

Correctness:
The first colored node x separates the tree into exactly three independent
regions. The second player can capture an entire chosen region by picking its
adjacent node. A majority region guarantees more nodes than player one can
obtain, and without a majority no first move for player two can win.

Complexity:
O(n) time and O(h) recursion space.

Edge cases:
- x is root: parent side has size 0.
- x is leaf: left and right sizes are 0.
*/
