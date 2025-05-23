import os.path
import pandas as pd
from pathlib import Path
from .config_module import read_config_setting

original_columns = ['cut', 'color', 'clarity', 'carat', 'depth', 'table', 'price',
                       'width', 'height', 'length']
numeric_columns = ['carat', 'depth', 'table', 'price',
                       'width', 'height', 'length']

def get_data_frame(use_volume:bool = False) -> pd.DataFrame:
    """
    Loads data from CSV file into DataFrame and returns the same.
    :param use_volume: if set to true, included derived feature volume in DataFrame,
    instead of features 'width', 'height', 'length'
    :return: DataFrame holding data from CSV file
    """
    # Read data source file location from yaml file
    file_path = read_config_setting('data_file')
    current_directory = Path(__file__).resolve().parent
    parent_directory = current_directory.parent.parent

    # Read data set
    dataset = pd.read_csv(os.path.join(parent_directory, file_path))

    # Dataset description
    # cut ['Fair' 'Good' 'Ideal' 'Premium' 'Very Good']
    # color ['E' 'F' 'H' 'G' 'J' 'I' 'D']
    # clarity ['VS2' 'SI2' 'SI1' 'I1' 'VVS1' 'VS1' 'IF' 'VVS2']
    # 'carat',depth,table,price,x (Premium),z (Very Good),y (Good)  Numeric columns
    # the depth and table percentages are key indicators of a diamond’s overall cut quality
    # if a diamond is too deep or too shallow it may not reflect light effectively making it
    # appear dull or less vibrant - Non-linear
    # width length and height measurements also contribute to the weight/carat distribution of the diamond
    # which in turn affects its price


    # Rename Columns
    dataset.columns = original_columns

    # In current dataset we got some of the records with length/width/height as zero, as there are max 20 such records,
    # lets remove them
    zero_value_columns = ['width', 'height', 'length']
    dataset = dataset[~((dataset[zero_value_columns] <= 0).any(axis=1))]

    # Perform label encoding for categorical variables
    # Order all below categories from worst to best
    cut_order = ['Fair', 'Good', 'Very Good', 'Premium', 'Ideal']
    color_order = ['J', 'I', 'H', 'G', 'F', 'E', 'D']
    clarity_order = ['I1', 'SI2', 'SI1', 'VS2', 'VS1', 'VVS2', 'VVS1', 'IF']

    # Apply label encoding
    cut_mapping = {cut: idx for idx, cut in enumerate(cut_order)}
    color_mapping = {color: idx for idx, color in enumerate(color_order)}
    clarity_mapping = {clarity: idx for idx, clarity in enumerate(clarity_order)}

    dataset['cut_encoded'] = dataset['cut'].map(cut_mapping)
    dataset['color_encoded'] = dataset['color'].map(color_mapping)
    dataset['clarity_encoded'] = dataset['clarity'].map(clarity_mapping)

    if use_volume:
        dataset['volume'] = dataset['width'] * dataset['height'] * dataset['length']
        dataset.drop(columns=zero_value_columns, inplace=True, axis=1)

    # Move price column to the end
    column_to_reorder = 'price'
    reordered_columns = [col for col in dataset.columns if col != column_to_reorder] + [column_to_reorder]
    dataset = dataset[reordered_columns]

    return dataset
