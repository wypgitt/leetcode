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
    bool escapeGhosts(vector<vector<int>>& ghosts, vector<int>& target) {
        int myDist = abs(target[0]) + abs(target[1]);
        for (auto& g : ghosts) {
            if (abs(g[0] - target[0]) + abs(g[1] - target[1]) <= myDist) return false;
        }
        return true;
    }
};

/*
Interview explanation:
If any ghost can reach the target no later than the player, it can wait at the target and catch the player. Otherwise going straight to the target succeeds.

C++ data structures: scalar Manhattan-distance calculations only.

Edge cases: equal distance is losing for the player.

Complexity: O(g) time and O(1) space.
*/
