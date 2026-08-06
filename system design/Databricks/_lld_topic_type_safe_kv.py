from _lld_topics import register
from _lld_sections import (
    build_doc, header, section_1, section_2, section_3, section_4,
    section_5, section_6, section_7, section_8, section_9, section_10,
    section_11, section_12,
)
from _lld_appendices import common_appendices


def build_type_safe_kv() -> str:
    return build_doc([
        header(
            "Generic Type-Safe Key-Value Store API",
            "Templates/generics · TypeRegistry · Serializer · TypeTag · Runtime type safety · Schema evolution",
            "Compile-time types where possible; explicit TypeMismatch at runtime; no silent casts",
        ),
        section_1(
            goal="Design a **generic KV store** where keys and values are typed (C++ templates / Java generics style), with runtime schema checks when types are erased.",
            what_is="""| Scope | Single-process typed KV facade | Raw byte[] map only |
| Typing | Per-key TypeTag + Serializer | Untyped everything |
| Safety | put/get with compile-time K,V where possible | Dynamic cast without checks |
| Databricks lens | Metadata/config stores with mixed types | Full SQL engine |""",
            fr_rows=[
                ("Key/value types?", "String keys; values: int, long, double, String, POJO, List", "TypeRegistry + Serializer per type"),
                ("Compile-time safety?", "Yes for generic API; runtime for dynamic paths", "TypeTag on stored blob"),
                ("Thread safety?", "Required", "RW lock or striped locks"),
                ("Persistence?", "Optional Phase 2; MVP in-memory", "Length-prefixed typed bytes"),
                ("Schema evolution?", "Add new types; old readers skip unknown tags", "Version in TypeTag"),
                ("Null values?", "Disallowed or explicit Optional", "Document absent vs null"),
                ("Max value size?", "Bounded (e.g. 1MB serialized)", "Reject oversize at put"),
                ("Delete semantics?", "remove(key) removes entry", "Counter per type optional"),
                ("Iteration?", "Optional keys() / scan by prefix", "Not MVP hot path"),
                ("Error on wrong get type?", "TypeMismatchException", "Never return wrong type silently"),
                ("Registration?", "Types registered at startup", "TypeId enum or string name"),
                ("Performance?", "Millions ops/s in-memory", "Avoid reflection on hot path"),
            ],
            mvp=[
                "Generic `TypedKVStore<K,V>` with compile-time K,V for put/get.",
                "`TypeRegistry` maps TypeTag → Serializer.",
                "Runtime storage as `Map<K, TypedBlob>` where blob = tag + bytes.",
                "`get<K,V>(key, Class<V>)` validates tag before deserialize.",
                "Thread-safe put/get/remove with documented linearization.",
                "Explicit `TypeMismatchError` when tag ≠ requested type.",
            ],
            scope="Single-node typed KV: generic API surface, TypeRegistry, serializers, runtime tag checks, thread-safe in-memory map, no silent type coercion.",
            invariant="""For every successful get<K,V>(k):
  stored.tag == registry.tag(V) AND deserialize(stored.bytes) yields value of type V.
put<K,V>(k,v) atomically replaces any prior value; tag always matches serializer(V).
No get returns a value whose runtime tag mismatches the requested type.""",
        ),
        section_2(
            api="""class TypedKVStore:
  TypedKVStore(TypeRegistry registry)
  <K, V> void put(K key, V value) throws SerializationException
  <K, V> Optional<V> get(K key, Class<V> type) throws TypeMismatchException
  <K, V> boolean remove(K key)
  boolean contains(K key)
  Set<K> keys()
  void close()

class TypeRegistry:
  <T> void register(Class<T> type, Serializer<T> ser)
  TypeTag tagOf(Class<?> type)
  Serializer<?> serializer(TypeTag tag)

interface Serializer<T>:
  byte[] serialize(T value)
  T deserialize(byte[] bytes)

class TypedBlob:
  TypeTag tag
  byte[] payload
  long version""",
            guarantees=[
                ("Type safety (static)", "put/get with same compile-time V cannot mismatch"),
                ("Type safety (dynamic)", "get(key, Class<V>) throws if stored tag ≠ V"),
                ("Single-key atomicity", "put/remove are atomic per key"),
                ("Linearizability", "Per-key ops linearizable under lock"),
                ("No silent coercion", "Never auto-convert int→string etc."),
                ("Serialization round-trip", "get after put returns equal value (equals)"),
            ],
            errors="""TypeMismatchException   — get requested type ≠ stored TypeTag
SerializationException  — serialize/deserialize failure
InvalidArgumentException — null key, oversize value
ClosedException         — ops after close
UnknownTypeTagException — tag not in registry""",
        ),
        section_3(
            classes=[
                ("TypedKVStore", "Public generic API; delegates to storage"),
                ("TypeRegistry", "Class→TypeTag, TypeTag→Serializer map"),
                ("TypeTag", "Stable id for runtime type identity"),
                ("Serializer<T>", "Encode/decode value to bytes"),
                ("TypedBlob", "Stored record: tag + payload"),
                ("StorageEngine", "Concurrent map K → TypedBlob"),
                ("Metrics", "puts/gets/mismatches by type"),
            ],
            diagram="""Client → TypedKVStore → TypeRegistry (tagOf, serializer)
                ↓
           StorageEngine: K → TypedBlob(tag, bytes)
                ↑ get validates tag before deserialize""",
        ),
        section_4("""### 4.1 TypeTag and Serializer

Stored header: `[tag_id:4][len:4][payload...]`. Registry frozen before serve.

| Op | Time | Notes |
|----|------|-------|
| put | O(1) + serialize | Replace whole blob |
| get | O(1) + deserialize | Tag check first |
| remove | O(1) | |

### 4.2 Compile-time vs runtime

Static: `Optional<V> get(K k)` with template/generic V.
Dynamic: `get(k, User.class)` checks tag at runtime.

### 4.3 C++ template sketch

```text
template<typename V>
void put(K k, V v) { map[k] = Blob{Tag<V>::id, serialize(v)}; }
```"""),
        section_5(
            "| map | RWLock or stripes |\n| TypeRegistry | immutable post-init |",
            ["Stored tag matches serializer at put.", "TypedBlob bytes immutable.", "Tag check before deserialize.", "close rejects new ops."],
            "serialize outside lock → lock(key) → map.put",
        ),
        section_6([
            ("put", """tag = registry.tagOf(value.class)
payload = registry.serializer(tag).serialize(value)
lock(key): map.put(key, TypedBlob(tag, payload))"""),
            ("get", """blob = map.get(key); if null: return empty
if blob.tag != registry.tagOf(typeClass): throw TypeMismatch
return deserialize(blob.payload)"""),
            ("register", """registry.register(User.class, UserSerializer)
registry.freeze()"""),
        ]),
        section_7([
            ("Wrong type get", "TypeMismatch", "No wrong object returned"),
            ("Unknown tag", "UnknownTypeTag", "Migration or purge"),
            ("Corrupt bytes", "SerializationException", "Remove entry policy"),
            ("Concurrent puts", "LWW", "Tag from last put"),
        ]),
        section_8(
            ["put String get String OK", "put int get String → TypeMismatch", "overwrite changes type/tag", "round-trip POJO", "null key rejected"],
            ["N threads distinct keys", "same key concurrent puts", "TSan clean"],
        ),
        section_9("Striped locks; pre-serialize outside lock; specialized primitive maps at 10×."),
        section_10(
            ["TypeRegistry + TypeTag on every blob", "Runtime tag check before deserialize", "No silent casts"],
            [("In-memory typed map", "Disk + migration"), ("Runtime class get", "C++-only static API")],
            ["Deserialize before tag check", "Mutable shared byte[]", "Registry drift across processes"],
        ),
        section_11(
            ["vs Map<String,Object>?", "Protobuf vs custom Serializer?", "Schema evolution?", "Avoid reflection?", "Polymorphic types?"],
            [("Just cast Object", "Check TypeTag"), ("Strings for everything", "Use typed API")],
        ),
        section_12(common_appendices("type-safe-kv-api", extra=[
            ("F. Example TypeTag table", "| 1 | int | 2 | String | 3 | UserProfile |"),
        ])),
    ])


register("type-safe-kv-api-lld-system-design.md", build_type_safe_kv)
