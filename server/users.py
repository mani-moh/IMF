from abc import ABC

class User(ABC):
    def __init__(self, user_id=int(), username=str(), hashed_password=bytes(), first_name=str(), last_name=str(), personnel_files_access=False, nuclear_codes_access=False, biological_files_access=False, is_dummy=True):
        self.id = user_id
        self.username = username
        self.hashed_password = hashed_password
        self.first_name = first_name
        self.last_name = last_name
        self.personnel_files_access = personnel_files_access
        self.nuclear_codes_access = nuclear_codes_access
        self.biological_files_access = biological_files_access
        self.is_dummy = is_dummy

