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
    int minKnightMoves(int x, int y) {
        memo.clear();
        return dfs(abs(x), abs(y));
    }

private:
    map<pair<int, int>, int> memo;

    int dfs(int x, int y) {
        x = abs(x);
        y = abs(y);
        if (x < y) swap(x, y);
        if (x == 0 && y == 0) return 0;
        if (x == 1 && y == 0) return 3;
        if (x == 1 && y == 1) return 2;

        pair<int, int> key = {x, y};
        if (memo.count(key)) return memo[key];
        return memo[key] = 1 + min(dfs(x - 1, y - 2), dfs(x - 2, y - 1));
    }
};

/*
Interview Explanation

Core idea:
The board is symmetric across axes and diagonals, so solve only for
x >= y >= 0. A knight reaching (x,y) must come from either (x-1,y-2) or
(x-2,y-1), after symmetry normalization.

C++ data structures:
- map<pair<int,int>, int> memo caches normalized states.

Algorithm:
1. Normalize coordinates with abs and x >= y.
2. Handle small special cases: (0,0), (1,0), and (1,1).
3. Recursively take one knight move backward and memoize the minimum.

Correctness:
Symmetry preserves knight distances, so normalization does not change the
answer. For non-base states, an optimal path's last move can be reversed to one
of the two predecessor forms after normalization. Trying both and adding one
therefore gives the optimal distance.

Complexity:
The number of memoized states is O(x*y) in the explored region, but the
recursive reduction is fast for constraints. Space matches memo size.

Edge cases:
- (1,0) requires 3 moves, a classic exception.
- Negative targets are normalized by symmetry.
*/
