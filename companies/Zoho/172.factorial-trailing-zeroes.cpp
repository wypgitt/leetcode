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
    int trailingZeroes(int n) {
        /*
        Approach: each trailing zero comes from a factor pair 2*5. Factor 2 is
        abundant, so count factors of 5 in n!: floor(n/5) + floor(n/25) + ... .

        Complexity: O(log_5 n) time, O(1) space.
        */
        int count = 0;
        while (n > 0) {
            n /= 5;
            count += n;
        }
        return count;
    }
};
