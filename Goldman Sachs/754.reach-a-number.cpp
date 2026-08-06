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
    int reachNumber(int target) {
        target = abs(target);
        int step = 0, sum = 0;
        while (sum < target || (sum - target) % 2 != 0) {
            ++step;
            sum += step;
        }
        return step;
    }
};

/*
Interview explanation:
After k moves the all-positive position is S=k(k+1)/2. Flipping chosen moves subtracts twice their sum, so target is reachable exactly when S>=target and S-target is even.

C++ data structures: scalar counters only.

Edge cases: negative targets are symmetric; target zero returns zero.

Complexity: O(sqrt(target)) time and O(1) space.
*/
