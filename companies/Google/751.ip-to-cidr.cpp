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
    long long ipToLong(const string& ip) {
        stringstream ss(ip);
        string part;
        long long value = 0;
        while (getline(ss, part, '.')) value = value * 256 + stoi(part);
        return value;
    }

    string longToIp(long long x) {
        return to_string((x >> 24) & 255) + "." + to_string((x >> 16) & 255) + "." + to_string((x >> 8) & 255) + "." + to_string(x & 255);
    }

public:
    vector<string> ipToCIDR(string ip, int n) {
        long long start = ipToLong(ip);
        vector<string> ans;
        while (n > 0) {
            long long lowbit = start & -start;
            if (lowbit == 0) lowbit = 1LL << 32;
            long long block = lowbit;
            while (block > n) block >>= 1;
            int prefix = 32 - (int)log2(block);
            ans.push_back(longToIp(start) + "/" + to_string(prefix));
            start += block;
            n -= block;
        }
        return ans;
    }
};

/*
Interview explanation:
Convert IPs to 32-bit integers. At each step choose the largest aligned power-of-two block that does not exceed the remaining count.

C++ data structures: long long safely stores 2^32 and address arithmetic; stringstream parses octets.

Edge cases: address zero has lowbit zero, so it is treated as aligned to the whole IPv4 range.

Complexity: O(number of CIDR blocks * 32) time worst case and output space for the blocks.
*/
