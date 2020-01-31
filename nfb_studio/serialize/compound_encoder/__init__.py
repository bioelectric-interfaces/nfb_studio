"""A set of functions that produce encoders/decoders capable of combining several encoders into one."""
from .encoder import compound_encoder
from .decoder import compound_decoder_hook, compound_decoder
