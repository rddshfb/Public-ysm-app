from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.clock import Clock
from plyer import filechooser
import os
from jnius import autoclass
from android.permissions import request_permissions, Permission
from android.storage import primary_external_storage_path

def decrypt_ysm(data):
    key = b"YSM2024"
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

class DecryptLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [dp(20) for dp in [20,20,20,20]]
        self.spacing = dp(15)
        self.canvas.before.add(Color(0,0,0,1))
        self.file_path = None
        self.decrypted_data = None
        
        self.build_ui()

    def build_ui(self):
        self.label = Label(text="YSM模型解密工具", color=(1,1,1,1), 
                          font_size='20sp', size_hint_y=None, height=dp(50))
        self.add_widget(self.label)

        self.select_btn = Button(text="选择加密文件", background_color=(0.2,0.2,0.2,1), 
                               color=(1,1,1,1), size_hint_y=None, height=dp(50))
        self.select_btn.bind(on_press=self.request_permissions_then_select)
        self.add_widget(self.select_btn)

        self.decrypt_btn = Button(text="一键解密", background_color=(0.2,0.2,0.2,1), 
                                color=(1,1,1,1), size_hint_y=None, height=dp(50))
        self.decrypt_btn.bind(on_press=self.decrypt_file)
        self.add_widget(self.decrypt_btn)

        self.save_btn = Button(text="导出保存", background_color=(0.2,0.2,0.2,1), 
                             color=(1,1,1,1), size_hint_y=None, height=dp(50))
        self.save_btn.bind(on_press=self.save_file)
        self.add_widget(self.save_btn)

    def request_permissions_then_select(self, instance):
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE
        ])
        Clock.schedule_once(lambda dt: self.select_file(instance), 1)

    def select_file(self, instance):
        try:
            if filechooser.open_file:
                filechooser.open_file(on_selection=self.on_file_selected)
            else:
                self.show_popup("提示", "文件选择器不可用，请手动输入路径")
        except:
            self.show_popup("错误", "文件选择失败")

    def on_file_selected(self, selection):
        if selection:
            self.file_path = selection[0]
            self.label.text = f"已选择: {os.path.basename(self.file_path)}"

    def decrypt_file(self, instance):
        if not self.file_path:
            self.show_popup("提示", "请先选择文件")
            return
        try:
            with open(self.file_path, 'rb') as f:
                data = f.read()
            self.decrypted_data = decrypt_ysm(data)
            self.label.text = "解密完成！点击导出保存"
        except Exception as e:
            self.show_popup("解密失败", str(e))

    def save_file(self, instance):
        if not self.decrypted_data:
            self.show_popup("提示", "请先解密文件")
            return
        try:
            downloads_path = primary_external_storage_path() + "/Download/"
            save_path = downloads_path + "YSM_decrypted.ysm"
            os.makedirs(downloads_path, exist_ok=True)
            with open(save_path, 'wb') as f:
                f.write(self.decrypted_data)
            self.show_popup("成功", f"已保存到:\nDownloads/YSM_decrypted.ysm")
        except Exception as e:
            self.show_popup("保存失败", str(e))

    def show_popup(self, title, msg):
        content = Label(text=msg, color=(1,1,1,1), halign="center", valign="middle")
        content.bind(size=content.setter('text_size'))
        popup = Popup(title=title, content=content, size_hint=(0.9, 0.5),
                     background_color=(0.1,0.1,0.1,0.9))
        popup.open()

class YSMDecryptApp(App):
    def build(self):
        from kivy.metrics import dp
        from kivy.graphics import Color
        return DecryptLayout()

YSMDecryptApp().run()