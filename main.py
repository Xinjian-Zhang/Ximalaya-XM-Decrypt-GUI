import base64
import io
import magic
import pathlib
import os
import glob
import mutagen
import tkinter as tk
from tkinter import filedialog, messagebox
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from mutagen.easyid3 import ID3
from wasmer import Store, Module, Instance, Uint8Array, Int32Array, engine
from wasmer_compiler_cranelift import Compiler
import webbrowser


class XMInfo:
    def __init__(self):
        self.title = ""
        self.artist = ""
        self.album = ""
        self.tracknumber = 0
        self.size = 0
        self.header_size = 0
        self.ISRC = ""
        self.encodedby = ""
        self.encoding_technology = ""

    def iv(self):
        if self.ISRC != "":
            return bytes.fromhex(self.ISRC)
        return bytes.fromhex(self.encodedby)


def get_str(x):
    if x is None:
        return ""
    return x


def read_file(x):
    with open(x, "rb") as f:
        return f.read()

def get_xm_info(data: bytes):
    id3 = ID3(io.BytesIO(data), v2_version=3)
    id3value = XMInfo()
    id3value.title = str(id3["TIT2"])
    id3value.album = str(id3["TALB"])
    id3value.artist = str(id3["TPE1"])
    id3value.tracknumber = int(str(id3["TRCK"]))
    id3value.ISRC = "" if id3.get("TSRC") is None else str(id3["TSRC"])
    id3value.encodedby = "" if id3.get("TENC") is None else str(id3["TENC"])
    id3value.size = int(str(id3["TSIZ"]))
    id3value.header_size = id3.size
    id3value.encoding_technology = str(id3["TSSE"])
    return id3value


def get_printable_count(x: bytes):
    for i, c in enumerate(x):
        if c < 0x20 or c > 0x7e:
            return i
    return i


def get_printable_bytes(x: bytes):
    return x[:get_printable_count(x)]


def xm_decrypt(raw_data):
    xm_encryptor = Instance(Module(
        Store(engine.Universal(Compiler)),
        pathlib.Path("./xm_encryptor.wasm").read_bytes()
    ))
    xm_info = get_xm_info(raw_data)
    encrypted_data = raw_data[xm_info.header_size:xm_info.header_size + xm_info.size:]

    xm_key = b"ximalayaximalayaximalayaximalaya"
    cipher = AES.new(xm_key, AES.MODE_CBC, xm_info.iv())
    de_data = cipher.decrypt(pad(encrypted_data, 16))

    de_data = get_printable_bytes(de_data)
    track_id = str(xm_info.tracknumber).encode()
    stack_pointer = xm_encryptor.exports.a(-16)
    de_data_offset = xm_encryptor.exports.c(len(de_data))
    track_id_offset = xm_encryptor.exports.c(len(track_id))
    memory_i = xm_encryptor.exports.i
    memview_unit8: Uint8Array = memory_i.uint8_view(offset=de_data_offset)
    for i, b in enumerate(de_data):
        memview_unit8[i] = b
    memview_unit8: Uint8Array = memory_i.uint8_view(offset=track_id_offset)
    for i, b in enumerate(track_id):
        memview_unit8[i] = b

    xm_encryptor.exports.g(stack_pointer, de_data_offset, len(de_data), track_id_offset, len(track_id))
    memview_int32: Int32Array = memory_i.int32_view(offset=stack_pointer // 4)
    result_pointer = memview_int32[0]
    result_length = memview_int32[1]
    assert memview_int32[2] == 0, memview_int32[3] == 0
    result_data = bytearray(memory_i.buffer)[result_pointer:result_pointer + result_length].decode()

    decrypted_data = base64.b64decode(xm_info.encoding_technology + result_data)
    final_data = decrypted_data + raw_data[xm_info.header_size + xm_info.size::]
    return xm_info, final_data


def find_ext(data):
    exts = ["m4a", "mp3", "flac", "wav"]
    value = magic.from_buffer(data).lower()
    for ext in exts:
        if ext in value:
            return ext
    raise Exception(f"unexpected format {value}")


def decrypt_xm_file(from_file, output_path='./output'):
    data = read_file(from_file)
    info, audio_data = xm_decrypt(data)
    output = f"{output_path}/{replace_invalid_chars(info.album)}/{replace_invalid_chars(info.title)}.{find_ext(audio_data[:0xff])}"
    if not os.path.exists(f"{output_path}/{replace_invalid_chars(info.album)}"):
        os.makedirs(f"{output_path}/{replace_invalid_chars(info.album)}")
    buffer = io.BytesIO(audio_data)
    tags = mutagen.File(buffer, easy=True)
    tags["title"] = info.title
    tags["album"] = info.album
    tags["artist"] = info.artist
    tags.save(buffer)
    with open(output, "wb") as f:
        buffer.seek(0)
        f.write(buffer.read())
    return output


def replace_invalid_chars(name):
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        if char in name:
            name = name.replace(char, " ")
    return name


def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    root.destroy()
    return file_path


def select_directory():
    root = tk.Tk()
    root.withdraw()
    directory_path = filedialog.askdirectory()
    root.destroy()
    return directory_path


def single_file_decrypt():
    file_to_decrypt = select_file()
    output_dir_path = output_dir()
    if file_to_decrypt:
        decrypted_file = decrypt_xm_file(file_to_decrypt, output_dir_path)
        tk.messagebox.showinfo("转换完成", f"已将文件转为在 {decrypted_file}")
    else:
        print("未选择文件")


def batch_decrypt():
    dir_to_decrypt = select_directory()
    output_dir_path = output_dir()  # Get the output directory path
    if dir_to_decrypt:
        files_to_decrypt = glob.glob(os.path.join(dir_to_decrypt, "*.xm"))
        for file in files_to_decrypt:
            decrypted_file = decrypt_xm_file(file, output_dir_path)

        tk.messagebox.showinfo("转换完成", f"已将文件转为在 {output_dir_path}")
    else:
        print("未选择目录")

def output_dir():
    root = tk.Tk()
    root.withdraw()
    directory_path = filedialog.askdirectory(title="选择输出文件夹")
    root.destroy()
    return directory_path

def show_author_info():
    messagebox.showinfo("关于作者", "GUI窗体: Xinjian-Zhang\n 解密算法及源码: Diaoxiaozhang")

def open_github():
    webbrowser.open("https://github.com/Xinjian-Zhang/Ximalaya-XM-Decrypt-GUI")

def main():
    root = tk.Tk()
    root.title("喜马拉*音频解密工具")
    root.geometry("300x180")

    single_file_button = tk.Button(root, text="解密单个文件", command=single_file_decrypt)
    single_file_button.pack(pady=10)

    batch_button = tk.Button(root, text="批量解密文件", command=batch_decrypt)
    batch_button.pack(pady=10)


    exit_button = tk.Button(root, text="退出", command=root.quit)
    exit_button.pack(pady=10)

    menubar = tk.Menu(root)
    about_menu = tk.Menu(menubar, tearoff=0)

    about_menu.add_command(label="作者信息", command=show_author_info)
    about_menu.add_separator()
    about_menu.add_command(label="GitHub", command=open_github)
    root.config(menu=menubar)
    menubar.add_cascade(label="关于", menu=about_menu)

    root.mainloop()


if __name__ == "__main__":
    main()
