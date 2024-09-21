# handler methods for managing contact data in variable dicts

class UsersWebDb:
    # In-memory storage for threads, initialized with a blank entry for user_id '0'
    threads = {"0": {}}

    @classmethod
    def check_thread_exists(cls):
        """"""
        return "0" in cls.threads

    @classmethod
    def create_new_thread(cls):
        """"""
        if "0" not in cls.threads:
            cls.threads["0"] = {}
            return True
        return False
