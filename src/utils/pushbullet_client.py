from pushbullet import Pushbullet

API_KEY = 'API_KEY'


class PushbulletClient:
    def __init__(self):
        self.__pb = Pushbullet(API_KEY)
        self.__emails = ['yonatankreiner@gmail.com', 'ariel042cohen@gmail.com', 'shay.mail@gmail.com']

    def push(self, body, title):
        for email in self.__emails:
            self.__pb.push_note(body=body, email=email, title=title)
