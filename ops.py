import param
from holoviews import Operation, Dataset
from holoviews.operation import column_interfaces, Element, RangeXY
import numpy as np


class dmate(Operation):
    """
    Decimates any column based Element to a specified number of random
    rows if the current element defined by the x_range and y_range
    contains more than max_samples. By default the operation returns a
    DynamicMap with a RangeXY stream allowing dynamic downsampling.
    """

    dynamic = param.Boolean(default=True, doc="""
       Enables dynamic processing by default.""")

    link_inputs = param.Boolean(default=True, doc="""
         By default, the link_inputs parameter is set to True so that
         when applying shade, backends that support linked streams
         update RangeXY streams on the inputs of the shade operation.""")

    max_samples = param.Integer(default=5000, doc="""
        Maximum number of samples to display at the same time.""")

    random_seed = param.Integer(default=42, doc="""
        Seed used to initialize randomization.""")

    streams = param.List(default=[RangeXY], doc="""
        List of streams that are applied if dynamic=True, allowing
        for dynamic interaction with the plot.""")

    x_range = param.NumericTuple(default=None, length=2, doc="""
       The x_range as a tuple of min and max x-value. Auto-ranges
       if set to None.""")

    y_range = param.NumericTuple(default=None, length=2, doc="""
       The x_range as a tuple of min and max y-value. Auto-ranges
       if set to None.""")

    def _process_layer(self, element, key=None):
        if not isinstance(element, Dataset):
            raise ValueError("Cannot downsample non-Dataset types.")
        if element.interface not in column_interfaces:
            element = element.clone(tuple(element.columns().values()))

        xstart, xend = self.p.x_range if self.p.x_range else element.range(0)
        ystart, yend = self.p.y_range if self.p.y_range else element.range(1)

        # Slice element to current ranges
        xdim, ydim = element.dimensions(label=True)[0:2]
        sliced = element.select(**{xdim: (xstart, xend),
                                   ydim: (ystart, yend)})

        # if len(sliced) > self.p.max_samples:
        #     prng = np.random.RandomState(self.p.random_seed)
        #     return sliced.iloc[prng.choice(len(sliced), self.p.max_samples, False)]
        return sliced

    def _process(self, element, key=None):
        return element.map(self._process_layer, Element)
