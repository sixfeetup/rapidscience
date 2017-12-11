def past_tense_verb(action):
    action_map = {
        'submit': 'submitted',
        'send back': 'sent back',
        'author review edit': 're-edited',
        'revise': 'pulled for revision',
    }
    verb = action.lower()
    if verb in action_map:
        return action_map[verb]
    if verb.endswith('e'):
        return verb + 'd'
    return verb + 'ed'
