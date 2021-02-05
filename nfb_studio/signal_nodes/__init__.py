from .lsl_input import LSLInput
from .spatial_filter import SpatialFilter
from .bandpass_filter import BandpassFilter
from .envelope_detector import EnvelopeDetector
from .standardise import Standardise
from .derived_signal_export import DerivedSignalExport
from .composite_signal_export import CompositeSignalExport
from .artificial_delay import ArtificialDelay

node_types = {
    "LSL Input": LSLInput,
    "Spatial Filter": SpatialFilter,
    "Bandpass Filter": BandpassFilter,
    "Envelope Detector": EnvelopeDetector,
    "Standardise": Standardise,
    "Artificial Delay": ArtificialDelay,
    "Derived Signal Export": DerivedSignalExport,
    "Composite Signal Export": CompositeSignalExport,
}