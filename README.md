# Legacy Revitalizer Exercise

## Overview

This exercise starts with a legacy interactive Python script and walks through a structured refactor.

The script behavior is a simple CLI workflow:

1. Prompts for username and password.
2. If credentials are valid, allows commands:
   - add: add an item with timestamp
   - show: print current items
   - save: persist items to file
   - exit: finish the app
3. If credentials are invalid, prints an error and exits.

The objective of the refactor was to keep core behavior while improving code quality and aligning the implementation with SOLID principles.

The final refactored version also includes security and reliability improvements for credential handling, input validation, and file persistence.

## Original Version

Source file: old-version/original_process_data.py

```python
import datetime

# Global variables (Bad practice)
l = []
d = {"u": "admin", "p": "12345"}


def fn(a, b):
	# Cryptic function that does too many things
	global l
	if a == "add":
		# Hardcoded logic and no validation
		t = datetime.datetime.now().strftime("%Y-%m-%d\n%H:%M:%S")
		l.append({"id": len(l) + 1, "val": b, "date": t})
		print("Added.")
	elif a == "show":
		for i in l:
			# Poor formatting
			print(
				"Item: "
				+ str(i["id"])
				+ " - "
				+ str(i["val"])
				+ " at "
				+ i["date"]
			)
	elif a == "save":
		# Direct file manipulation without context manager
		f = open("data.txt", "w")
		f.write(str(l))
		f.close()
		print("Saved.")


def check(u, p):
	# Insecure authentication logic
	if u == d["u"] and p == d["p"]:
		return True
	else:
		return False


# Execution flow is messy and unprotected
u_in = input("User: ")
p_in = input("Pass: ")

if check(u_in, p_in):
	print("Welcome")
	while True:
		cmd = input("What to do? (add/show/save/exit): ")
		if cmd == "exit":
			break
		if cmd == "add":
			v = input("Value: ")
			fn("add", v)
		else:
			fn(cmd, None)
else:
	print("Wrong!")


# More dead code or redundant logic
def calculate_something_else(x):
	# This is never used
	res = 0
	for i in range(x):
		res += i
	return res
```

## Refactors Applied And Why

### 1) Stabilization and formatting pass

What changed:
- Fixed broken indentation and line wrapping so the code became valid and readable Python.

Why:
- The legacy file had malformed structure that made it hard to run and maintain.

Impact:
- Kept behavior equivalent in the stabilization step.

### 2) Removed global variables

What changed:
- Replaced global item list and credentials dict with object state:
  - credentials moved to AuthenticationService
  - item storage moved to ItemRepository

Why:
- Global mutable state creates hidden coupling and makes testing difficult.

Impact:
- No change in expected login and item management behavior.

### 3) Replaced multi-purpose function with dedicated services

What changed:
- Broke legacy fn(a, b) into specific use cases in ItemService:
  - add_item
  - show_items
  - save_items

Why:
- One function doing many jobs violates Single Responsibility and complicates changes.

Impact:
- Command mapping remained add/show/save.

### 4) Introduced a domain model

What changed:
- Added Item dataclass with fields:
  - item_id
  - value
  - created_at

Why:
- Typed, explicit structure is easier to reason about than loose dictionaries.

Impact:
- Internal data model improved while preserving user-visible output semantics.

### 5) Isolated persistence

What changed:
- Added JsonFileItemWriter for file output.
- Replaced manual open/write/close with context manager.
- Used json.dump with dataclasses.asdict serialization.

Why:
- Persistence should be separate from business logic.
- Context managers are safer and prevent resource leaks.

Impact:
- Save output is now formatted JSON in data.txt instead of str(list).

### 6) Added repository abstraction

What changed:
- Added ItemRepository with:
  - add(value)
  - list_all()
- list_all returns a copy to prevent accidental external mutation.

Why:
- Encapsulation protects internal state and enables easier backend swaps later.

Impact:
- Functional behavior stayed the same for current CLI flow.

### 7) Isolated authentication concerns

What changed:
- Replaced check(u, p) + global credentials with AuthenticationService.authenticate.

Why:
- Clear auth boundary and better future extensibility (hashing, external auth).

Impact:
- Current credentials and success/failure behavior remain equivalent.

### 8) Encapsulated app orchestration

What changed:
- Added Application class responsible only for interaction flow and command loop.

Why:
- Separating orchestration from business logic improves maintainability.

Impact:
- Core interaction flow preserved.
- Unknown command now reports an explicit message.

### 9) Added explicit entry point

What changed:
- Added main() and module guard.

Why:
- Prevents side effects when importing the module.

Impact:
- Script execution behavior remains normal when run directly.

### 10) Removed dead code

What changed:
- Removed unused calculate_something_else function from refactored target.

Why:
- Dead code adds noise and maintenance cost.

Impact:
- No runtime behavior change for user workflow.

### 11) Secured credential flow with environment variables

What changed:
- Removed hardcoded credentials from the refactored runtime path.
- Added environment-based configuration with:
	- APP_USERNAME
	- APP_PASSWORD

Why:
- Hardcoded credentials are a security risk and do not adapt to different environments.

Impact:
- The refactored script now requires environment variables before startup.

### 12) Hardened authentication checks

What changed:
- Credential comparisons use hmac.compare_digest.

Why:
- Reduces timing-leak risk compared to direct string equality.

Impact:
- Same success/failure behavior, safer comparison path.

### 13) Protected password input

What changed:
- Replaced visible password input with getpass.getpass in the refactored flow.

Why:
- Avoids exposing typed secrets on screen.

Impact:
- User experience remains similar but password is hidden.

### 14) Added input validation for add command

What changed:
- Added validation for item values:
	- trims whitespace
	- rejects empty values
	- rejects values longer than 500 characters

Why:
- Prevents invalid/abusive inputs and improves data quality.

Impact:
- Invalid input now returns a user-friendly error message.

### 15) Improved save reliability with atomic writes

What changed:
- Save now writes to a temp file and then replaces the target file atomically.
- Output directory is created automatically when missing.

Why:
- Reduces chance of partial/corrupted output files during failures.

Impact:
- Save path is more resilient while preserving command behavior.

### 16) Added runtime error handling in command loop

What changed:
- Added explicit handling for ValueError and OSError in the refactored command loop.

Why:
- Provides clearer user feedback and prevents abrupt crashes for expected failures.

Impact:
- Application responds with readable error messages and continues running.

## SOLID Alignment Summary

- Single Responsibility: each class has one focused responsibility.
- Open/Closed: behavior can be extended with new services/writers.
- Liskov Substitution: components can be replaced with compatible implementations.
- Interface Segregation: small focused APIs replaced a broad utility function.
- Dependency Inversion: dependencies are composed in main, avoiding hidden globals.

## How To Run

### Requirements

- Python 3.10 or newer recommended.
- Git Bash terminal (examples below use Git Bash syntax).
- Environment variables for refactored version:
	- APP_USERNAME
	- APP_PASSWORD

### Run original version

From project root:

```bash
python old-version/original_process_data.py
```

### Run refactored version

From project root in Git Bash:

```bash
export APP_USERNAME="admin"
export APP_PASSWORD="your-strong-password"
python process_data.py
```

### Optional: persist variables in Git Bash profile

Add to ~/.bashrc (or ~/.bash_profile):

```bash
export APP_USERNAME="admin"
export APP_PASSWORD="your-strong-password"
```

Then reload shell configuration:

```bash
source ~/.bashrc
```

### Runtime notes

- The original legacy script still uses its internal hardcoded credentials.
- The refactored script requires APP_USERNAME and APP_PASSWORD.
- If env vars are missing, the refactored script exits with a configuration error.
- In the refactored script, password entry is hidden.

### CLI commands after login

- add
- show
- save
- exit

## Exercise Outcome

The exercise demonstrates how to evolve a legacy, global-state script into a more maintainable and testable architecture while preserving the user workflow and improving separation of concerns.
