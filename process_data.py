import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


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

        return username == self._username and password == self._password


class ItemRepository:
    """Stores and retrieves items in memory."""

    def __init__(self) -> None:
        """Create an empty in-memory item collection."""

        self._items: list[Item] = []

    def add(self, value: str) -> None:
        """Create and store a new item using the provided value."""

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item = Item(item_id=len(self._items) + 1, value=value, created_at=timestamp)
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
        """Serialize the given items and write them to disk as JSON."""

        serializable_items = [asdict(item) for item in items]
        with self._output_path.open("w", encoding="utf-8") as file_obj:
            json.dump(serializable_items, file_obj, indent=2)


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
        password = input("Pass: ")

        if not self._auth_service.authenticate(username, password):
            print("Wrong!")
            return

        print("Welcome")
        while True:
            command = input("What to do? (add/show/save/exit): ")
            if command == "exit":
                break
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


def main() -> None:
    """Compose dependencies and start the CLI application."""

    auth_service = AuthenticationService(username="admin", password="12345")
    repository = ItemRepository()
    writer = JsonFileItemWriter(output_path=Path("data.txt"))
    item_service = ItemService(repository=repository, writer=writer)
    app = Application(auth_service=auth_service, item_service=item_service)
    app.run()


if __name__ == "__main__":
    main()
