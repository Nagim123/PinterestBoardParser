class PinterestBoardDoesNotExistException(Exception):
    def __init__(self, board_name: str, board_owner: str) -> None:
        super().__init__(f"Failed to load board '{board_name}' of user '{board_owner}' from pinterest.com")