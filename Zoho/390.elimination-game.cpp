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
    int lastRemaining(int n) {
        int head = 1, step = 1, remaining = n;
        bool leftToRight = true;
        while (remaining > 1) {
            if (leftToRight || remaining % 2 == 1) head += step;
            remaining /= 2;
            step *= 2;
            leftToRight = !leftToRight;
        }
        return head;
    }
};

/*
Interview explanation:
After every deletion round the survivors form an arithmetic sequence. Track its first value, the gap, the remaining count, and the direction. The first value moves on every left-to-right pass and on right-to-left passes with odd survivor count.

C++ data structures: scalar integers are enough; building a list would be wasteful.

Edge cases: n=1 returns 1 immediately.

Complexity: O(log n) time because the count halves each round, and O(1) space.
*/
