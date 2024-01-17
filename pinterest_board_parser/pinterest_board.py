import requests
import json
import os
import re
import urllib.parse
from bs4 import BeautifulSoup
from .pinterest_pin import PinterestPin
from .pinterest_parse_logger import get_parsing_logger

class PinterestBoard():
    """
    Class that represent Pinterest board.
    """

    def __init__(self, user_name: str, board_name: str, cache_file_path: str = None) -> None:
        """
        Create new PinterestBoard object by providing name of board and owner user.

        Parameters:
            user_name (str): User name of a board owner.
            board_name (str): Name of board itself.
            cache_file_path (str): Path to cache file.
        """
        self.__logger = get_parsing_logger()
        self.__logger.info(f"Initializing board {board_name} of user {user_name}")

        self.__user_name = user_name
        self.__board_name = board_name
        self.__board_id = self.__parse_board_id()

        self.__cache_file_path = cache_file_path
        
        self.__pin_list: list[PinterestPin] = []

        
        if cache_file_path is not None:
            if not os.path.exists(cache_file_path):
                self.__logger.info("Can't find cache file. New one will be created.")
            else:
                self.__logger.info("Loading cached board data from a file")
                self.__load_from_file()

    def get_pins(self) -> list[PinterestPin]:
        """
        Get all pins from a board.

        Returns:
            list[PinterestPin]: List of pins from a board.
        """

        self.__parse_and_cache_new_pins()
        return self.__pin_list
    
    def __parse_and_cache_new_pins(self) -> None:
        """
        Parse new pins that appear in a board and caches them.
        """
        PINTEREST_BOARD_RESOURCES_URL = "https://pinterest.com/resource/BoardFeedResource/get/"
        
        bookmarks = []
        video_search_pattern = re.compile(r'https:\/\/[^ ,"]+\.mp4')
        found_cached_pin = False

        parsed_pins_list = []

        self.__logger.info("Start parsing new pins!")
        while not found_cached_pin:
            parsed_pins_count = 0
            OPTIONS = {
                "options": {
                    "board_id": str(self.__board_id),
                    "board_url": urllib.parse.quote(f"/{self.__user_name}/{self.__board_name}/"),
                    "currentFilter": -1,
                    "field_set_key": "react_grid_pin",
                    "filter_section_pins": True,
                    "sort": "default",
                    "layout": "default",
                    "page_size": 25,
                    "redux_normalize_feed": True,
                    "bookmarks": bookmarks,
                    "context": {}
                }
            }
            response = requests.get(f"{PINTEREST_BOARD_RESOURCES_URL}?data={urllib.parse.quote(json.dumps(OPTIONS).encode("UTF-8"), safe='')}")
            json_data = response.json()
            pin_data = json_data["resource_response"]["data"]
            for pin in pin_data:
                pinterest_pin = PinterestPin(pin["images"]["orig"]["url"], pin["id"], pin["grid_title"], self.__board_name, self.__user_name)
                
                if pinterest_pin in self.__pin_list:
                    found_cached_pin = True
                    break
                
                # Check if pin actually has a video
                matched_video_url = video_search_pattern.search(json.dumps(pin))
                if matched_video_url is not None:
                    pinterest_pin.resource_link = matched_video_url.group(0)

                parsed_pins_list.append(pinterest_pin)
                parsed_pins_count += 1
            
            if "bookmark" in json_data["resource_response"]:
                bookmarks = [json_data["resource_response"]["bookmark"]]
            else:
                break

            self.__logger.info(f"Batch of {parsed_pins_count} pins was parsed successfully!")
        
        parsed_pins_list.reverse()
        self.__pin_list.extend(parsed_pins_list)

        if self.__cache_file_path is not None:
            self.__save_to_file()

    def __parse_board_id(self) -> int:
        """
        Parse board ID from HTML of a board page.

        Returns:
            int: Board ID.
        """

        self.__logger.info("Sending request to PINTEREST API to get board id.")
        response = requests.get(f"https://pinterest.com/{self.__user_name}/{self.__board_name}")

        self.__logger.info("Parsing response in format of HTML page")
        soup = BeautifulSoup(response.text, "html.parser")
        pws_json_data = json.loads(soup.find(id="__PWS_DATA__").text)

        if not "BoardFeedResource" in pws_json_data["props"]["initialReduxState"]["resources"]:
            raise Exception(f"Board with name '{self.__board_name}' and owner name '{self.__user_name}' was not found.")

        self.__logger.info("Extracting board id from parsed data")
        board_data = list(pws_json_data["props"]["initialReduxState"]["resources"]["BoardFeedResource"].keys())[0]
        board_id = int(board_data.split(',')[1].split('=')[1].replace('"', ''))
        
        return board_id

    def __save_to_file(self) -> None:
        """
        Save board data into a file.
        """
        self.__logger.info("Saving board to a file...")

        board_dict = dict()
        board_dict["user_name"] = self.__user_name
        board_dict["board_name"] = self.__board_name
        board_dict["pin_list"] = str(self.__pin_list)
        with open(self.__cache_file_path, "w", encoding="UTF-8") as cache_file:
            cache_file.write(str(board_dict))

        self.__logger.info("Board successfully saved to a cache file!")

    def __load_from_file(self) -> None:
        """
        Load board data from a file.
        """
        self.__logger.info("Loading board from file...")

        with open(self.__cache_file_path, "r", encoding="UTF-8") as cache_file:
            try:
                board_dict = eval(cache_file.read())
            except:
                raise Exception(f"File {self.__cache_file_path} is corrupted")
            if self.__user_name != board_dict["user_name"] or self.__board_name != board_dict["board_name"]:
                raise Exception(
                    f"Cache file {self.__cache_file_path} contains data about board {board_dict['board_name']} of user {board_dict['user_name']}, but not about board {self.__board_name} of user {self.__user_name}"
                )
            
            self.__pin_list = eval(board_dict["pin_list"])
        
        self.__logger.info("Board successfully loaded from a file!")
    
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, PinterestBoard):
            return self.__board_name == __value.__board_name and self.__user_name == __value.__user_name
        return False