from abc import abstractmethod
from typing import *

import csv
from matplotlib import pyplot as plt  # type: ignore


class BasePlot:
  @abstractmethod
  def add_cell(self, indep_val: float, data: str) -> None:
    raise NotImplementedError()

  @abstractmethod
  def render(self, subplot: Any) -> None:
    raise NotImplementedError()


class LinePlot(BasePlot):
  def __init__(self) -> None:
    self.x_values: List[float] = []
    self.y_values: List[float] = []

  def add_cell(self, indep_val: float, data: str) -> None:
    self.x_values.append(indep_val)
    self.y_values.append(float(data))

  def render(self, subplot: Any) -> None:
    pass


class WaterfallPlot(BasePlot):
  def __init__(self) -> None:
    self.x_values: List[float] = []
    self.y_values: List[List[float]] = []

  def add_cell(self, indep_val: float, data: str) -> None:
    self.x_values.append(indep_val)
    self.y_values.append([float(arr_elt) for arr_elt in data[1:-1].split(',')])

  def render(self, subplot: Any) -> None:
    pass


def str_is_float(input: str) -> bool:
  if not input:  # TODO: this is a bit hacky, we default empty cell as float
    return True
  try:
    float(input)
    return True
  except ValueError:
    return False


def str_is_array(input: str) -> bool:
  return len(input) > 1 and input[0] == '[' and input[-1] == ']'


if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser(description='CSV Telemetry / Logger Visualizer')

  parser.add_argument('filename',
                      help='filename of CSV to open, the first column is treated as the independent axis')
  parser.add_argument('--merge', '-m', action='append', default=[],
                      help='column names to merge for each plot, comma-separated without spaces, '
                           'can be specified multiple times, eg "-m camera,line -m kp,kd"')
  parser.add_argument('--skip_data_rows', type=int, default=0,
                      help='data columns to skip')
  args = parser.parse_args()

  #
  # Parse the input CSV
  #
  with open(args.filename, newline='') as csvfile:
    reader = csv.reader(csvfile)
    names = next(reader)

    try:
      for _ in range(args.skip_data_rows):  # skip skipped rows
        next(reader)

      data_row = next(reader)  # infer data type from first row
      plots: List[BasePlot] = []
      for col_name, data_cell in zip(names[1:], data_row[1:]):  # discard first col
        if str_is_float(data_cell):
          print(f"detected numeric / line plot for '{col_name}'")
          plot: BasePlot = LinePlot()
        elif str_is_array(data_cell):
          print(f"detected array / waterfall plot for '{col_name}'")
          plot = WaterfallPlot()
        else:
          raise ValueError(f"Unable to infer data type for '{col_name}' from data contents '{data_cell}'")
        plots.append(plot)

      data_row_idx = 0
      print(f"working: parsed {data_row_idx} rows", end='\r')
      while True:
        indep_value = float(data_row[0])
        for data_col_idx, data_cell in enumerate(data_row[1:]):  # discard first col
          if data_cell:
            plots[data_col_idx].add_cell(indep_value, data_cell)

        data_row_idx += 1
        if data_row_idx % 1000 == 0:
          print(f"working: parsed {data_row_idx} rows", end='\r')

        data_row = next(reader)

    except StopIteration:
      print(f"finished: parsed {data_row_idx} rows")

  #
  # Build plots
  #
  merge_sets = [frozenset(arg.split(',')) for arg in args.merge]  # use frozenset since it's hashable
  merge_dict: Dict[str, FrozenSet[str]] = {}
  for merge_set in merge_sets:
    for merge_item in merge_set:
      merge_dict[merge_item] = merge_set

  #
  # Render graphs
  #

  plt.show()


