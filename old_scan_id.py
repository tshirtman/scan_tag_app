def scan_id(self, otype=None, get_uuid4=False):
    if otype is None:
        # WORFLOWS
        if self.target_entry['otype'] == 'shelf':
            print("last item was a shelf.. what now?")
            self.switch_screen("entries")
            return
        elif self.target_entry['otype'] == 'set':
            otype = 'box'
        elif self.target_entry['otype'] == 'box':
            otype = 'part'
        elif self.target_entry['otype'] == 'part':
            otype = 'part'
