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
    int movesToMakeZigzag(vector<int>& nums) {
        return min(cost(nums, 0), cost(nums, 1));
    }

private:
    int cost(const vector<int>& nums, int valleyParity) {
        int moves = 0;
        int n = nums.size();

        for (int i = valleyParity; i < n; i += 2) {
            int neighborMin = INT_MAX;
            if (i > 0) neighborMin = min(neighborMin, nums[i - 1]);
            if (i + 1 < n) neighborMin = min(neighborMin, nums[i + 1]);
            if (neighborMin != INT_MAX && nums[i] >= neighborMin) {
                moves += nums[i] - neighborMin + 1;
            }
        }

        return moves;
    }
};

/*
Interview Explanation

Core idea:
In a zigzag array, either even indices are valleys or odd indices are valleys.
Because we can only decrement values, compute the cost for both patterns.

C++ data structures:
- No extra structure is needed; a helper scans the vector and accumulates cost.

Algorithm:
For a chosen valley parity, each valley index must be strictly smaller than
both neighbors. If nums[i] is too large, decrement it to neighborMin - 1.
Take the minimum cost across the two parity choices.

Correctness:
Every zigzag arrangement has exactly one of the two valley parity patterns.
For a fixed pattern, changing a valley lower never hurts other valley
constraints, and reducing it just enough is optimal. Therefore the helper gives
the minimum for that pattern, and the minimum of both patterns is global.

Complexity:
O(n) time and O(1) space.

Edge cases:
- Single element needs 0 moves.
- Boundary valleys have only one neighbor.
*/
