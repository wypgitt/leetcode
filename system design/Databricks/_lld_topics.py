"""Registry for LLD topic document builders."""

ALL_BUILDERS: list[tuple[str, callable]] = []


def register(filename: str, builder) -> None:
    ALL_BUILDERS.append((filename, builder))
