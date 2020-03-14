"""NFB experiment designer."""
from .serial import json, hooks

std_encoder = json.JSONEncoder(hooks=hooks.qt, indent='\t')
std_decoder = json.JSONDecoder(hooks=hooks.qt)