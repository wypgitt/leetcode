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
    int findDerangement(int n) {
        const long long MOD = 1000000007;
        if (n == 1) return 0;
        long long prev2 = 1, prev1 = 0;
        for (int i = 2; i <= n; ++i) {
            long long cur = (i - 1) * (prev1 + prev2) % MOD;
            prev2 = prev1;
            prev1 = cur;
        }
        return prev1;
    }
};

/*
Interview explanation:
Derangements satisfy D(n)=(n-1)*(D(n-1)+D(n-2)). Track only the previous two DP values.

C++ data structures: long long prevents overflow before applying the modulus.

Edge cases: D(1)=0 and D(0)=1 are recurrence bases.

Complexity: O(n) time and O(1) space.
*/
