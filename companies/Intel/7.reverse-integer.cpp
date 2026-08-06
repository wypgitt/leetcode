#include <algorithm>
#include <cctype>
#include <climits>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <sstream>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>
using namespace std;


class Solution {
public:
    int reverse(int x) {
        /*
        Approach:
        Repeatedly pop the last decimal digit from x and append it to the
        reversed value. Store the intermediate result in long long so overflow
        can be detected before returning a 32-bit int.

        Complexity: O(number of digits) time and O(1) space.
        */
        long long ans = 0;
        while (x != 0) {
            ans = ans * 10 + x % 10;
            x /= 10;
            if (ans < INT_MIN || ans > INT_MAX) return 0;
        }
        return (int)ans;
    }
};
