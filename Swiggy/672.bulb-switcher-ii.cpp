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
public:
    int flipLights(int n, int presses) {
        n = min(n, 6);
        set<vector<int>> seen;
        for (int mask = 0; mask < 16; ++mask) {
            int bits = __builtin_popcount((unsigned)mask);
            if (bits > presses || ((presses - bits) & 1)) continue;
            vector<int> state;
            for (int i = 1; i <= n; ++i) {
                int on = 1;
                if (mask & 1) on ^= 1;
                if ((mask & 2) && i % 2 == 0) on ^= 1;
                if ((mask & 4) && i % 2 == 1) on ^= 1;
                if ((mask & 8) && i % 3 == 1) on ^= 1;
                state.push_back(on);
            }
            seen.insert(state);
        }
        return seen.size();
    }
};

/*
Interview explanation:
Only button parity matters because pressing the same button twice cancels. Enumerate 16 parity masks; a mask is reachable if it uses no more presses and has matching parity with the number of presses.

C++ data structures: set<vector<int>> stores distinct states. Only first six bulbs matter because patterns repeat every lcm(2,3)=6.

Edge cases: zero presses admits only the initial state.

Complexity: O(1) time and space because 16 masks and at most 6 bulbs are considered.
*/
