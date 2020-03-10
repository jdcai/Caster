from dragonfly import Repeat, MappingRule

from castervoice.lib.actions import Key

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.additions import IntegerRefST
from castervoice.lib.merge.state.short import R


class SlackRule(MappingRule):
    mapping = {
    
        "quick switch": R(Key("c-k")),
        "next focus": R(Key("f6")),
        "back focus": R(Key("s-f6")),
        "direct messages": R(Key("cs-k")),
        "browse all channels": R(Key("cs-l")),
        "thread view": R(Key("cs-t")),
        "back unread": R(Key("as-up")),
        "next unread": R(Key("as-down")),
        "back channel": R(Key("a-left")),
        "next channel": R(Key("a-right")),
        "previous search": R(Key("c-g")),
        "open unread": R(Key("cs-a")),
        # Workspace
        "back workspace": R(Key("cs-tab")),
        "next workspace": R(Key("c-tab")),
        "workspace <n>": R(Key("c-%(n)s"))
    }
    extras = [
        IntegerRefST("n", 1, 10),
    ]
    defaults = {"n": 1}


def get_rule():
    return SlackRule, RuleDetails(name="slack", executable="slack")
