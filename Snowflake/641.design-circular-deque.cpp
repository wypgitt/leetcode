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

class MyCircularDeque {
    vector<int> data;
    int capacity, frontIndex, count;

public:
    MyCircularDeque(int k) : data(k), capacity(k), frontIndex(0), count(0) {}

    bool insertFront(int value) {
        if (isFull()) return false;
        frontIndex = (frontIndex - 1 + capacity) % capacity;
        data[frontIndex] = value;
        ++count;
        return true;
    }

    bool insertLast(int value) {
        if (isFull()) return false;
        int rear = (frontIndex + count) % capacity;
        data[rear] = value;
        ++count;
        return true;
    }

    bool deleteFront() {
        if (isEmpty()) return false;
        frontIndex = (frontIndex + 1) % capacity;
        --count;
        return true;
    }

    bool deleteLast() {
        if (isEmpty()) return false;
        --count;
        return true;
    }

    int getFront() { return isEmpty() ? -1 : data[frontIndex]; }

    int getRear() { return isEmpty() ? -1 : data[(frontIndex + count - 1) % capacity]; }

    bool isEmpty() { return count == 0; }

    bool isFull() { return count == capacity; }
};

/*
Interview explanation:
A fixed circular buffer supports O(1) insert/delete at both ends. frontIndex points to the first element and count derives both rear and fullness.

C++ data structures: vector<int> owns contiguous fixed capacity storage; modular arithmetic wraps indices.

Edge cases: get operations return -1 when empty; deleteLast only decrements count because stale values can be overwritten.

Complexity: all operations O(1), space O(k).
*/
