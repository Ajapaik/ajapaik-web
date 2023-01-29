class AddAdditionalSubjectData:
    gender = None
    age = None
    subject_annotation_rectangle_id = None
    new_subject_id = None

    def __init__(self, subject_rectangle_id: int, age: int, gender: int, new_subject_id: int | None = None):
        self.subject_annotation_rectangle_id = subject_rectangle_id
        self.age = age
        self.gender = gender
        self.new_subject_id = new_subject_id
