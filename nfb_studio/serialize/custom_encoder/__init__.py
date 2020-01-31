"""An encoder/decoder pair that allows for registering types that can be encoded."""
from .encoder import CustomEncoder
from .decoder import CustomDecoder, generate_custom_decoder_hook
