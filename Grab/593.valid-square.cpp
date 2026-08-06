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
    int dist2(const vector<int>& a, const vector<int>& b) {
        int dx = a[0] - b[0], dy = a[1] - b[1];
        return dx * dx + dy * dy;
    }

public:
    bool validSquare(vector<int>& p1, vector<int>& p2, vector<int>& p3, vector<int>& p4) {
        vector<vector<int>> p = {p1, p2, p3, p4};
        vector<int> d;
        for (int i = 0; i < 4; ++i) for (int j = i + 1; j < 4; ++j) d.push_back(dist2(p[i], p[j]));
        sort(d.begin(), d.end());
        return d[0] > 0 && d[0] == d[1] && d[1] == d[2] && d[2] == d[3] && d[4] == d[5] && d[4] == 2 * d[0];
    }
};

/*
Interview explanation:
A square has four equal positive side distances and two equal diagonal distances, with diagonal squared equal to twice side squared.

C++ data structures: vector<int> holds the six squared pairwise distances.

Edge cases: duplicate points produce zero side length and are rejected.

Complexity: O(1) time and space.
*/
