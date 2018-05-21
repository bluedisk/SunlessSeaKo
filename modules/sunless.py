EXCLUDE_OBJECTS = (
    # events
    'LinkToEvent', 'Deck', 'LimitedToArea', 
    'QualitiesAffected', 'QualitiesRequired', 
    'Setting', 'SwitchToSetting',

    # exchange
    'Availabilities',

    # qualities
    'AssignToSlot',
    'AssociatedQuality',
    'UseEvent',
)


class RecursiveProcessor:
    def __init__(self):
        self.processed = 0
        self.notprocessed = 0
        
    def process(self, root):
        self.processed = 0
        self.notprocessed = 0
        
        self._recusive_process(root, 'root')
        
        return self.processed, self.notprocessed
    
    def _process_node(self, node, parentName):
        return False

    def _recusive_process(self, node, parentName):
        if type(node) == dict:
            if node.get('Id', None) and (
                    (node.get('Name', None) and node['Name'].strip()) or
                    (node.get('Teaser', None) and node['Teaser'].strip()) or
                    (node.get('Description', None) and node['Description'].strip())
            ):
                if self._process_node(node, parentName):
                    self.processed += 1
                else:
                    self.notprocessed += 1

            for k, v in node.items():
                if k not in EXCLUDE_OBJECTS:
                    self._recusive_process(v, k)

        elif type(node) == list:
            for item in node:
                self._recusive_process(item, parentName)


class RecursiveUpdateProcessor(RecursiveProcessor):

    def __init__(self):
        super(RecursiveUpdateProcessor, self).__init__()
        self.trans_dict = {}

    def process(self, root, trans_dict):
        self.trans_dict = trans_dict
        return super(RecursiveUpdateProcessor, self).process(root)

    def _process_node(self, node, parentName):
        node_id = node['Id']
        trans = self.trans_dict.get(str(node_id), None)
        if not trans:
            return False

        node['Name'] = trans['Name']
        node['Teaser'] = trans['Teaser']
        node['Description'] = trans['Description']

        if not node['Teaser']:
            temp_teaset = node['Description'].split('.')[0][:40]
            node['Teaser'] = temp_teaset

        return True


def diff_tree(old_dict, new_dict):
    changed_count = 0
    
    for k, v in new_dict.items():
        value = old_dict.get(k, None)
        if not value or value != v:
            changed_count += 1

    return changed_count