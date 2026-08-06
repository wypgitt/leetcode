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
    double radius, xCenter, yCenter;
    mt19937 rng;
    uniform_real_distribution<double> dist;

public:
    Solution(double radius, double x_center, double y_center)
        : radius(radius), xCenter(x_center), yCenter(y_center), rng(random_device{}()), dist(0.0, 1.0) {}

    vector<double> randPoint() {
        const double PI = acos(-1.0);
        double angle = dist(rng) * 2.0 * PI;
        double r = radius * sqrt(dist(rng));
        return {xCenter + r * cos(angle), yCenter + r * sin(angle)};
    }
};

/*
Interview explanation:
Sample angle uniformly and radius as R*sqrt(U). The square root is necessary because circle area grows with r^2; choosing radius uniformly would over-sample the center.

C++ data structures: mt19937 plus uniform_real_distribution<double> provide reusable random generation.

Edge cases: all points are within the circle; boundary probability is negligible with continuous sampling.

Complexity: O(1) time and space per point.
*/
