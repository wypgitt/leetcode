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

class Solution {
public:
    vector<int> pathInZigZagTree(int label) {
        vector<int> path;
        while (label > 0) {
            path.push_back(label);
            int level = 31 - __builtin_clz(label);
            int levelStart = 1 << level;
            int levelEnd = (1 << (level + 1)) - 1;
            label = (levelStart + levelEnd - label) / 2;
        }
        reverse(path.begin(), path.end());
        return path;
    }
};

/*
Interview Explanation

Core idea:
In a normal binary tree, a node's parent is label / 2. In the zigzag-labelled
tree, each level is mirrored. Convert the current label to its mirrored normal
position, move to its parent, then repeat.

C++ data structures:
- vector<int> stores the path from node to root, then reverse gives root to node.
- Bit operations find the level quickly: floor(log2(label)).

Algorithm:
1. Push the current label into path.
2. Determine its level range [2^level, 2^(level+1)-1].
3. Mirror the label inside that level with start + end - label.
4. Divide by 2 to move to the parent in the previous level.
5. Reverse the collected path.

Correctness:
Mirroring maps a zigzag label to the label it would have in the normal
left-to-right level order. Dividing by 2 gives the true parent position.
Mirroring is symmetric, so the computed parent label is correct in zigzag
labelling. Repeating reaches the root and collects exactly the ancestor path.

Complexity:
The tree height is O(log label), so time and space are O(log label).

Edge cases:
- label = 1 returns [1].
- Labels on either end of a level mirror correctly because start/end are
  included in the formula.
*/
