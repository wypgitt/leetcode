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
    unordered_map<int, bool> memo;
    int maxInt;

    bool winning(int usedMask, int remaining) {
        if (memo.count(usedMask)) return memo[usedMask];
        for (int x = 1; x <= maxInt; ++x) {
            int bit = 1 << (x - 1);
            if (usedMask & bit) continue;
            if (x >= remaining || !winning(usedMask | bit, remaining - x)) return memo[usedMask] = true;
        }
        return memo[usedMask] = false;
    }

public:
    bool canIWin(int maxChoosableInteger, int desiredTotal) {
        if (desiredTotal <= 0) return true;
        if (maxChoosableInteger * (maxChoosableInteger + 1) / 2 < desiredTotal) return false;
        maxInt = maxChoosableInteger;
        memo.clear();
        return winning(0, desiredTotal);
    }
};

/*
Interview explanation:
The game state is the set of used numbers and the remaining total. The current player wins if one legal pick reaches the target or leaves the opponent in a losing state.

C++ data structures: an int bitmask compactly tracks used numbers; unordered_map memoizes reachable states.

Edge cases: if the sum of all numbers is too small, the first player cannot force a win.

Complexity: O(m*2^m) time and O(2^m) space for m=maxChoosableInteger.
*/
