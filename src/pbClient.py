from pushbullet import Pushbullet

API_KEY = 'o.17PPFbrT55nqMEezbrMCuR2iRpc895lE'


class PushbulletClient:
    def __init__(self):
        self.__pb = Pushbullet(API_KEY)
        self.__emails = ['yonatankreiner@gmail.com', 'ariel042cohen@gmail.com', 'shay.mail@gmail.com']

    def push(self, body, title):
        map(lambda email: self.__pb.push_note(body=body, email=email, title=title), self.__emails)
