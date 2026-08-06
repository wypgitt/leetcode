#include <algorithm>
#include <array>
#include <cctype>
#include <climits>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <sstream>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;


class Solution {
public:
    int minCost(vector<vector<int>>& costs) {
        /*
        Approach: rolling DP for three colors. The cost of painting current house
        red is redCost + min(previous blue, previous green), and similarly for
        the other colors.

        Complexity: O(n) time, O(1) space.
        */
        if (costs.empty()) return 0;
        int red = 0, blue = 0, green = 0;
        for (auto& cost : costs) {
            int prevRed = red, prevBlue = blue, prevGreen = green;
            red = cost[0] + min(prevBlue, prevGreen);
            blue = cost[1] + min(prevRed, prevGreen);
            green = cost[2] + min(prevRed, prevBlue);
        }
        return min({red, blue, green});
    }
};
