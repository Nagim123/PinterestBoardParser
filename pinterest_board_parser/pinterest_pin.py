from dataclasses import dataclass

@dataclass
class PinterestPin():
    """Class for storing Pinterest Pin Image related data"""
    resource_link: str
    pin_id: int
    title: str
    board_name: str
    board_author: str

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, PinterestPin):
            return self.pin_id == __value.pin_id
        return False