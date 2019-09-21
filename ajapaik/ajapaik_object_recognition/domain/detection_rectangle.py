def get_if_key_present(data, key):
    if key in data:
        return data[key]

    return None


class DetectionRectangle:
    def __init__(self, init):
        self.id = init['id']

        self.x1 = init['x1']
        self.y1 = init['y1']
        self.x2 = init['x2']
        self.y2 = init['y2']

        self.subjectId = get_if_key_present(init, 'subject_id')
        self.subjectName = get_if_key_present(init, 'subject_name')
        self.wikiDataId = get_if_key_present(init, 'wiki_data_id')
        self.translations = get_if_key_present(init, 'translations')
        self.isDeletable = get_if_key_present(init, 'is_deletable')
        self.hasUserGivenFeedback = get_if_key_present(init, 'has_user_given_feedback')
