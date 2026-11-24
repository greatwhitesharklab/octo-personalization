"""octo-flywheel — the data-flywheel layer over the octo personalization lever.

The plumbing is open glue (anyone can write it); the moat is the accumulated per-customer data
(memory + interaction log + outcome-weighted salience) you run through it — that stays yours.
Depends on the public octo-personalization.
"""
from .capture import InteractionLog, Interaction
from .writeback import extract_facts, write_back
from .consolidate import refresh_profile, salient_values, prune
from .feedback import update_salience, rank_facts
from .loop import Flywheel, StateStore

__version__ = '0.1.0'
__all__ = ['InteractionLog', 'Interaction', 'extract_facts', 'write_back',
           'refresh_profile', 'salient_values', 'prune', 'update_salience', 'rank_facts',
           'Flywheel', 'StateStore']
