
import requests


class MyTelegramBot():
    def __init__(self, token, channels = None) -> None:
        self.token = token
        self.listChannels = channels
        self.URL = "https://api.telegram.org"

        # print(self.bot_getMe())
        if not self.bot_getMe():
            raise Exception("Bot not existed")
        pass

    def bot_getMe(self):
        """Check if the bot is existed"""
        isExisted = False
        url = f'{self.URL}/bot{self.token}/getme'
        try:
            res = requests.get(url=url)
            print(res)
            if res.status_code == 200:
                print(res.json())
                if res.json()['result']['is_bot']:
                    isExisted = True
        except Exception as e:
            print(e)
        return isExisted

    def send_message(self, message, channel=None, parse_mode='MarkdownV2', disable_web_page_preview=None):
        """Send message to channel(s)"""
        response_str = ''
        error = False
        channels = self.listChannels
        if channel:
            channels = [channel]
        
        if not channels:
            response_str = 'No channel(s) configed'
        # https://api.telegram.org/bot5046667864:AAEH_FD7MKa4Dwoq5Zuoxk1Mmp76Y62DWUs
        # /sendMessage?chat_id=@GhoztBinance&parse_mode=HTML&disable_web_page_preview=1&text=
        for channel in channels:
            url = f'{self.URL}/bot{self.token}/sendMessage?text={message}&chat_id={channel}&parse_mode={parse_mode}'
            if disable_web_page_preview:
                url = f'{self.URL}/bot{self.token}/sendMessage?text={message}&chat_id={channel}&parse_mode={parse_mode}&disable_web_page_preview={disable_web_page_preview}'
            try:
                res = requests.get(url=url)
                print(res)
                if res.status_code == 200:
                    print(res.json())
                    response_str = res.json()
                    if not res.json()['ok']:
                        print(f"Error happened when sending to {channel}")
                        error = True
                else:
                    print(res.json())
                    response_str = res.json()
            except Exception as e:
                print(e)
                response_str = str(e)
        return response_str

    # TODO:
    # will add new functions/ methods. Update to use telegram library if we need more functions
