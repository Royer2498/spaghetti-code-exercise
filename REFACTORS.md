# Refactor Log: process_data.py

This document records all refactors applied from the legacy script to the current implementation.

## Scope

- Source baseline: old-version/original_process_data.py
- Current target: process_data.py
- Goal: preserve the command-line flow (login -> add/show/save/exit), improve structure, remove global variables, and align with SOLID principles.

## High-Level Evolution

1. Stabilization pass
- Fixed broken formatting and indentation so the script became valid, readable Python.
- Preserved original runtime behavior during this initial pass.

2. Architecture refactor pass
- Replaced procedural + global-state design with class-based composition.
- Introduced clear responsibilities per class and explicit dependency wiring in main().
- Removed global variables entirely.

## Detailed Refactors

### 1) Removed global variables

Legacy:
- Used global mutable list `l` for data storage.
- Used global dict `d` for credentials.

Refactor:
- Moved credential state into AuthenticationService instance fields.
- Moved item state into ItemRepository instance field (`self._items`).

Why:
- Globals create tight coupling and implicit dependencies.
- Instance state is explicit, testable, and easier to evolve.

Impact:
- Functional behavior remains equivalent for auth and in-memory item management.

### 2) Replaced multi-purpose function with dedicated services

Legacy:
- `fn(a, b)` handled add/show/save command logic in one function.

Refactor:
- `ItemService.add_item()` handles add flow.
- `ItemService.show_items()` handles presentation text generation.
- `ItemService.save_items()` delegates persistence.

Why:
- The old function violated single responsibility and made extensions error-prone.
- New design localizes behavior and reduces branching complexity.

Impact:
- User-facing commands still map to add/show/save semantics.

### 3) Introduced domain model with dataclass

Legacy:
- Stored each item as ad-hoc dictionaries.

Refactor:
- Added `Item` dataclass with fields:
  - `item_id`
  - `value`
  - `created_at`

Why:
- Stronger structure for item data.
- Better readability and maintainability.

Impact:
- Output semantics are preserved; internal representation is cleaner.

### 4) Separated persistence from business logic

Legacy:
- File I/O lived inside the command function.
- Used manual open/write/close.

Refactor:
- Added `JsonFileItemWriter` dedicated to persistence.
- Uses context manager (`with ... open(...)`) for safe file handling.
- Serializes to JSON via `json.dump` + `dataclasses.asdict`.

Why:
- Isolates infrastructure concerns from business logic.
- Safer resource management.

Impact:
- Save output format changed from Python list string to formatted JSON structure.
- File name remains `data.txt` to avoid workflow disruption.

### 5) Added repository abstraction for in-memory storage

Legacy:
- Direct list mutation from command function.

Refactor:
- `ItemRepository` encapsulates:
  - `add(value)`
  - `list_all()`
- Returns a copy from `list_all()` to avoid accidental external mutation.

Why:
- Encapsulation improves safety and future replaceability (e.g., DB-backed repo).

Impact:
- Behavior unchanged for current CLI usage.

### 6) Isolated authentication concerns

Legacy:
- `check(u, p)` depended on global credentials dict.

Refactor:
- `AuthenticationService.authenticate(username, password)` compares against injected values.

Why:
- Clear boundary for auth logic.
- Simplifies future enhancement (hashed passwords, external provider, etc.).

Impact:
- Same login success/failure behavior for current credentials.

### 7) Encapsulated application flow in Application class

Legacy:
- Top-level script logic executed on import and mixed orchestration with logic.

Refactor:
- `Application.run()` handles interaction loop.
- Command dispatch remains explicit and readable.
- Unknown commands now print `Unknown command`.

Why:
- Better orchestration separation and cleaner entry point.

Impact:
- Main flow preserved.
- Added explicit response for unsupported commands.

### 8) Added explicit entry point

Legacy:
- Immediate execution at module import time.

Refactor:
- Added `main()` and module guard:
  - `if __name__ == "__main__":`

Why:
- Prevents side effects on import.
- Improves testability and composability.

Impact:
- Normal script execution remains unchanged.

### 9) Removed dead code

Legacy:
- `calculate_something_else(x)` was unused.

Refactor:
- Removed unused function.

Why:
- Reduces noise and maintenance burden.

Impact:
- No runtime impact in existing flow.

## SOLID Mapping

### S - Single Responsibility Principle
- AuthenticationService: auth only.
- ItemRepository: item storage only.
- JsonFileItemWriter: persistence only.
- ItemService: item use-cases only.
- Application: CLI orchestration only.

### O - Open/Closed Principle
- New command behaviors or save targets can be added by extending services/writers with minimal core changes.

### L - Liskov Substitution Principle
- Current concrete classes are replaceable with compatible alternatives (e.g., a different writer/repository behavior) without changing orchestration intent.

### I - Interface Segregation Principle
- Consumers depend on small, focused method sets instead of a large utility function.

### D - Dependency Inversion Principle
- Application composes dependencies externally in `main()` rather than relying on global, hidden state.

## Behavior Notes and Compatibility

Preserved:
- Login prompt and welcome/failure flow.
- Interactive command loop and add/show/save/exit behavior.
- Timestamp format `%Y-%m-%d %H:%M:%S`.
- Incremental item IDs starting at 1.

Changed intentionally:
- `save` now writes JSON-formatted data (still in `data.txt`) instead of Python `str(list)` representation.
- Unknown command handling now returns a clear message.

## Potential Next Refactors (Optional)

1. Introduce Protocol interfaces for repository/writer/auth to make dependency inversion explicit at type level.
2. Replace plaintext credentials with environment variables and hashed secrets.
3. Add unit tests for AuthenticationService, ItemRepository, and ItemService.
4. Add input validation (empty values, max lengths).
5. Consider renaming `data.txt` to `data.json` for format clarity.
