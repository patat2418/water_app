import math
from config.config import Config
from pandas import DataFrame

def calculate_max_distance(pipes_table: DataFrame ):
    max_distance = 0
    for i, pipe1 in pipes_table.iterrows():
        for j, pipe2 in pipes_table.iterrows():
            if i != j:
                distance = math.sqrt(
                    (pipe1['start'][0] - pipe2['end'][0])**2 +
                    (pipe1['start'][1] - pipe2['end'][1])**2 +
                    (pipe1['start'][2] - pipe2['end'][2])**2
                )
                max_distance = max(max_distance, distance)
    return max_distance

def update_text_config(max_distance):
    min_text_size = Config.MIN_TEXT_SIZE
    max_text_size = Config.MAX_TEXT_SIZE
    min_distance = Config.MIN_DISTANCE
    max_allowed_distance = Config.MAX_ALLOWED_DISTANCE

    clamped_distance = max(min_distance, min(max_distance, max_allowed_distance))
    normalized_distance = math.log(clamped_distance) / math.log(max_allowed_distance)

    Config.TEXT_SIZE = round(min_text_size + (max_text_size - min_text_size) * normalized_distance, 1)
    Config.PADDING = Config.TEXT_SIZE +2 

    min_margin = 30
    max_margin = 120
    Config.MARGIN = round(min_margin + (max_margin - min_margin) * normalized_distance, 1)

def calculate_text_size(max_distance):
    min_text_size = 2.5
    max_text_size = 10
    min_distance = 10
    max_allowed_distance = 5000

    clamped_distance = max(min_distance, min(max_distance, max_allowed_distance))
    normalized_distance = math.log(clamped_distance) / math.log(max_allowed_distance)

    text_size = min_text_size + (max_text_size - min_text_size) * normalized_distance
    
    # חישוב ה-padding בהתאם לגודל הטקסט
    min_padding = 2
    max_padding = 8
    padding = min_padding + (max_padding - min_padding) * normalized_distance

    # חישוב ה-margin בהתאם לגודל הטקסט
    min_margin = 30
    max_margin = 120
    margin = min_margin + (max_margin - min_margin) * normalized_distance

    return round(text_size, 1), round(padding, 1), round(margin, 1)