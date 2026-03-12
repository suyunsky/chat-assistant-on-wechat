from wechatpy.enterprise import WeChatClient

from bridge.context import ContextType
from channel.chat_message import ChatMessage
from common.log import logger
from common.tmp_dir import TmpDir


class WechatComAppMessage(ChatMessage):
    def __init__(self, msg, client: WeChatClient, is_group=False):
        super().__init__(msg)
        self.msg_id = msg.id
        self.create_time = msg.time
        self.is_group = is_group

        if msg.type == "text":
            self.ctype = ContextType.TEXT
            self.content = msg.content
        elif msg.type == "voice":
            self.ctype = ContextType.VOICE
            self.content = TmpDir().path() + msg.media_id + "." + msg.format  # content直接存临时目录路径

            def download_voice():
                # 如果响应状态码是200，则将响应内容写入本地文件
                response = client.media.download(msg.media_id)
                if response.status_code == 200:
                    with open(self.content, "wb") as f:
                        f.write(response.content)
                else:
                    logger.info(f"[wechatcom] Failed to download voice file, {response.content}")

            self._prepare_fn = download_voice
        elif msg.type == "image":
            self.ctype = ContextType.IMAGE
            self.content = TmpDir().path() + msg.media_id + ".png"  # content直接存临时目录路径

            def download_image():
                # 如果响应状态码是200，则将响应内容写入本地文件
                response = client.media.download(msg.media_id)
                if response.status_code == 200:
                    with open(self.content, "wb") as f:
                        f.write(response.content)
                    logger.info(f"[wechatcom] Downloaded image file: {self.content}")    
                else:
                    logger.info(f"[wechatcom] Failed to download image file, {response.content}")

            self._prepare_fn = download_image
        elif msg.type == "file":
            self.ctype = ContextType.FILE
            # 获取文件名，企业微信文件消息可能有file_name属性
            file_name = getattr(msg, 'file_name', f'file_{msg.media_id}')
            # 保持原始文件扩展名
            if hasattr(msg, 'file_ext') and msg.file_ext:
                file_name = f'{file_name}.{msg.file_ext}'
            self.content = TmpDir().path() + file_name  # content直接存临时目录路径

            def download_file():
                # 如果响应状态码是200，则将响应内容写入本地文件
                response = client.media.download(msg.media_id)
                if response.status_code == 200:
                    with open(self.content, "wb") as f:
                        f.write(response.content)
                    logger.info(f"[wechatcom] Downloaded file: {file_name}")
                else:
                    logger.info(f"[wechatcom] Failed to download file, {response.content}")

            self._prepare_fn = download_file
        else:
            raise NotImplementedError("Unsupported message type: Type:{} ".format(msg.type))

        self.from_user_id = msg.source
        self.to_user_id = msg.target
        self.other_user_id = msg.source
