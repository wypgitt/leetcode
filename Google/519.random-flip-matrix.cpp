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
    int rows, cols, total, remaining;
    unordered_map<int, int> remap;
    mt19937 rng;

public:
    Solution(int m, int n) : rows(m), cols(n), total(m * n), remaining(m * n), rng(random_device{}()) {}

    vector<int> flip() {
        uniform_int_distribution<int> dist(0, remaining - 1);
        int pick = dist(rng);
        --remaining;
        int actual = remap.count(pick) ? remap[pick] : pick;
        remap[pick] = remap.count(remaining) ? remap[remaining] : remaining;
        return {actual / cols, actual % cols};
    }

    void reset() {
        remaining = total;
        remap.clear();
    }
};

/*
Interview explanation:
This is lazy Fisher-Yates over flattened matrix indices. Pick a random live slot, map it to its actual index, then move the last live slot into the picked position.

C++ data structures: unordered_map stores only remapped indices, avoiding O(mn) memory initialization; mt19937 provides random picks.

Edge cases: reset clears the map and restores the full live range.

Complexity: expected O(1) flip/reset and O(f) space after f flips.
*/
