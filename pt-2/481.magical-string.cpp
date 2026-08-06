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
    int magicalString(int n) {
        if (n <= 0) return 0;
        vector<int> s = {1, 2, 2};
        if (n <= 3) return count(s.begin(), s.begin() + n, 1);
        int read = 2, nextNum = 1, ones = 1;
        while ((int)s.size() < n) {
            int repeat = s[read++];
            for (int k = 0; k < repeat && (int)s.size() < n; ++k) {
                s.push_back(nextNum);
                if (nextNum == 1) ++ones;
            }
            nextNum = 3 - nextNum;
        }
        return ones;
    }
};

/*
Interview explanation:
The magical string describes its own run lengths. Starting from 122, a read pointer gives how many copies of the next alternating value to append.

C++ data structures: vector<int> stores generated digits because future positions are read as run lengths.

Edge cases: n<=3 is answered directly from the seed.

Complexity: O(n) time and O(n) space.
*/
