from pinterest_board_parser.pinterest_board import PinterestBoard

board = PinterestBoard(user_name="amutalapov", board_name="как-это-работает-я-не-понимаю-рандом-какой-то", cache_file_path="test.pinboard")
the_oldest_pin = board.get_pins()[0]

print(the_oldest_pin.pin_id)
print(the_oldest_pin.resource_link)
print(the_oldest_pin.title)