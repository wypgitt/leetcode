import java.util.*;

/**
 * Algorithm:
 * Combine a HashMap for key lookup with a doubly linked list for recency order.
 * The most recently used node sits before the tail sentinel; the least recently
 * used node sits after the head sentinel.
 *
 * Java data structures:
 * HashMap<Integer, Node> gives O(1) lookup. Custom linked nodes give O(1)
 * removal and insertion without relying on LinkedHashMap.
 *
 * Complexity:
 * get and put are O(1), space O(capacity).
 */
class LRUCache {
    private static class Entry {
        int key;
        int value;
        Entry prev;
        Entry next;

        Entry() {}

        Entry(int key, int value) {
            this.key = key;
            this.value = value;
        }
    }

    private final int capacity;
    private final Map<Integer, Entry> nodes;
    private final Entry head;
    private final Entry tail;

    public LRUCache(int capacity) {
        this.capacity = capacity;
        nodes = new HashMap<>();
        head = new Entry();
        tail = new Entry();
        head.next = tail;
        tail.prev = head;
    }

    public int get(int key) {
        Entry node = nodes.get(key);
        if (node == null) {
            return -1;
        }
        markUsed(node);
        return node.value;
    }

    public void put(int key, int value) {
        Entry node = nodes.get(key);
        if (node != null) {
            node.value = value;
            markUsed(node);
            return;
        }
        node = new Entry(key, value);
        nodes.put(key, node);
        addToBack(node);
        if (nodes.size() > capacity) {
            Entry lru = head.next;
            remove(lru);
            nodes.remove(lru.key);
        }
    }

    private void markUsed(Entry node) {
        remove(node);
        addToBack(node);
    }

    private void remove(Entry node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
    }

    private void addToBack(Entry node) {
        Entry last = tail.prev;
        last.next = node;
        node.prev = last;
        node.next = tail;
        tail.prev = node;
    }
}

