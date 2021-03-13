# Example of receiving an Android Share of .mp4 file or plain text.

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.videoplayer import VideoPlayer
from kivy.uix.label import Label
from sharercv import ShareRcv

class ShareReceiveExample(App):

    def build(self):
        self.label = Label(text='Share some text or video with me')
        self.video = VideoPlayer()
        box = BoxLayout(orientation='vertical')
        box.add_widget(self.video)
        box.add_widget(self.label)
        self.share_listener = ShareRcv(text_callback=self.new_text,
                                       video_callback=self.new_video)
        return box

    def new_text(self, text, MIMEtype):
        self.label.text  = text

    def new_video(self, source, MIMEtype):
        self.video.state  = 'stop'
        self.video.source = source
        self.video.state  = 'play'
    
    def on_pause(self):
        self.resume_state = self.video.state
        if self.video.state  == 'play':
            self.video.state  = 'pause'
        return True

    def on_resume(self):
        if self.resume_state == 'play':
            self.video.state = 'play'

ShareReceiveExample().run()


