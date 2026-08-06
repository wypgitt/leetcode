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
    int flipgame(vector<int>& fronts, vector<int>& backs) {
        unordered_set<int> banned;
        for (int i = 0; i < (int)fronts.size(); ++i) if (fronts[i] == backs[i]) banned.insert(fronts[i]);
        int ans = INT_MAX;
        for (int x : fronts) if (!banned.count(x)) ans = min(ans, x);
        for (int x : backs) if (!banned.count(x)) ans = min(ans, x);
        return ans == INT_MAX ? 0 : ans;
    }
};

/*
Interview explanation:
A value shown on both sides of the same card can never be hidden from all fronts, so it is banned. The smallest non-banned value appearing on any side is achievable.

C++ data structures: unordered_set<int> stores banned values.

Edge cases: if all values are banned, return 0.

Complexity: O(n) time and O(n) space.
*/
