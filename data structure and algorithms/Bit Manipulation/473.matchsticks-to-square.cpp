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

class Solution {
    int side;
    vector<int> sticks;
    array<int, 4> sides{};

    bool dfs(int i) {
        if (i == (int)sticks.size()) return sides[0] == side && sides[1] == side && sides[2] == side && sides[3] == side;
        int len = sticks[i];
        unordered_set<int> seen;
        for (int j = 0; j < 4; ++j) {
            if (sides[j] + len > side || seen.count(sides[j])) continue;
            seen.insert(sides[j]);
            sides[j] += len;
            if (dfs(i + 1)) return true;
            sides[j] -= len;
        }
        return false;
    }

public:
    bool makesquare(vector<int>& matchsticks) {
        int total = accumulate(matchsticks.begin(), matchsticks.end(), 0);
        if (matchsticks.size() < 4 || total % 4) return false;
        side = total / 4;
        sticks = matchsticks;
        sort(sticks.rbegin(), sticks.rend());
        if (sticks[0] > side) return false;
        sides = {0, 0, 0, 0};
        return dfs(0);
    }
};

/*
Interview explanation:
Backtracking assigns each stick to one of four equal-length sides. Sorting descending makes large restrictive sticks fail early, and skipping side sums already tried avoids symmetric duplicate states.

C++ data structures: array<int,4> is ideal for the four side sums; unordered_set<int> per level removes equivalent placements.

Edge cases: total must be divisible by four and no stick can exceed the side length.

Complexity: worst-case O(4^n), heavily pruned; recursion depth O(n).
*/
