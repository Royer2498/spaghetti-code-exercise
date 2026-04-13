import getpass
import hmac
import json
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class Item:
    """Represents a stored item with identifier, value, and creation timestamp."""

    item_id: int
    value: str
    created_at: str


class AuthenticationService:
    """Handles user credential validation for the CLI application."""

    def __init__(self, username: str, password: str) -> None:
        """Initialize the authentication service with expected credentials."""

        self._username = username
        self._password = password

    def authenticate(self, username: str, password: str) -> bool:
        """Return True when provided credentials match configured credentials."""

        return hmac.compare_digest(username, self._username) and hmac.compare_digest(
            password, self._password
        )


class ItemRepository:
    """Stores and retrieves items in memory."""

    def __init__(self) -> None:
        """Create an empty in-memory item collection."""

        self._items: list[Item] = []

    def add(self, value: str) -> None:
        """Create and store a new item using the provided value."""

        clean_value = value.strip()
        if not clean_value:
            raise ValueError("Value cannot be empty.")
        if len(clean_value) > 500:
            raise ValueError("Value is too long (max 500 characters).")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item = Item(item_id=len(self._items) + 1, value=clean_value, created_at=timestamp)
        self._items.append(item)

    def list_all(self) -> list[Item]:
        """Return a copy of all stored items."""

        return self._items.copy()


class JsonFileItemWriter:
    """Persists item collections to a JSON file."""

    def __init__(self, output_path: Path) -> None:
        """Initialize the writer with the output file path."""

        self._output_path = output_path

    def save(self, items: list[Item]) -> None:
        """Serialize items and write them atomically to disk as JSON."""

        serializable_items = [asdict(item) for item in items]
        self._output_path.parent.mkdir(parents=True, exist_ok=True)

        temp_path: Optional[Path] = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=str(self._output_path.parent),
                delete=False,
            ) as file_obj:
                json.dump(serializable_items, file_obj, indent=2)
                file_obj.flush()
                os.fsync(file_obj.fileno())
                temp_path = Path(file_obj.name)

            temp_path.replace(self._output_path)
        finally:
            if temp_path and temp_path.exists():
                temp_path.unlink(missing_ok=True)


class ItemService:
    """Coordinates item operations between repository and persistence layer."""

    def __init__(self, repository: ItemRepository, writer: JsonFileItemWriter) -> None:
        """Initialize the service with its data repository and writer."""

        self._repository = repository
        self._writer = writer

    def add_item(self, value: str) -> str:
        """Add a new item and return a user-facing status message."""

        self._repository.add(value)
        return "Added."

    def show_items(self) -> list[str]:
        """Build display lines for all stored items."""

        output: list[str] = []
        for item in self._repository.list_all():
            output.append(
                f"Item: {item.item_id} - {item.value} at {item.created_at}"
            )
        return output

    def save_items(self) -> str:
        """Persist all current items and return a user-facing status message."""

        self._writer.save(self._repository.list_all())
        return "Saved."


class Application:
    """Runs the command-line interaction flow for the application."""

    def __init__(
        self,
        auth_service: AuthenticationService,
        item_service: ItemService,
    ) -> None:
        """Initialize the app with authentication and item services."""

        self._auth_service = auth_service
        self._item_service = item_service

    def run(self) -> None:
        """Execute the interactive login and command loop."""

        username = input("User: ")
        password = getpass.getpass("Pass: ")

        if not self._auth_service.authenticate(username, password):
            print("Wrong!")
            return

        print("Welcome")
        while True:
            command = input("What to do? (add/show/save/exit): ").strip().lower()
            if command == "exit":
                break
            try:
                if command == "add":
                    value = input("Value: ")
                    print(self._item_service.add_item(value))
                    continue
                if command == "show":
                    for line in self._item_service.show_items():
                        print(line)
                    continue
                if command == "save":
                    print(self._item_service.save_items())
                    continue

                print("Unknown command")
            except ValueError as error:
                print(f"Error: {error}")
            except OSError as error:
                print(f"I/O error: {error}")


def main() -> None:
    """Compose dependencies and start the CLI application."""

    configured_username = os.getenv("APP_USERNAME")
    configured_password = os.getenv("APP_PASSWORD")
    if not configured_username or not configured_password:
        print("Configuration error: set APP_USERNAME and APP_PASSWORD environment variables.")
        return

    auth_service = AuthenticationService(
        username=configured_username,
        password=configured_password,
    )
    repository = ItemRepository()
    writer = JsonFileItemWriter(output_path=Path("data.txt"))
    item_service = ItemService(repository=repository, writer=writer)
    app = Application(auth_service=auth_service, item_service=item_service)
    app.run()


if __name__ == "__main__":
    main()
