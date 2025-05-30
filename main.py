import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
import tkinter.messagebox
import maliang as m
import tkinter.filedialog
from tkinter import messagebox
import pyperclip
import winreg

# 添加项目根目录到 Python 路径
# sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 导入转换器
from src.converter import BaseConverter

# 初始化全局变量
path_ = ""
pathf_ = None

def selectPath():
    global path_
    # 选择文件路径
    path_ = tkinter.filedialog.askopenfilename()
    # 使用 os.path.normpath 更安全地处理路径
    path_ = os.path.normpath(path_)
    
def selectFloder():
    global pathf_
    # 选择保存目录
    pathf_ = tkinter.filedialog.askdirectory()
    pathf_ = os.path.normpath(pathf_)


def covert():
    global pathf_, path_, con
    if (not path_) and con == None:
        tkinter.messagebox.showwarning("请先选择文件！")
        return
    try:
        if con == None:
            with open(path_, "r", encoding="utf-8-sig", errors='ignore') as f:
                c = f.read()
        else:
            c = con
        coverter = BaseConverter()
        doc = coverter.convert(c)

        if pathf_ == None:
            pathf_ = os.path.dirname(path_)
        if con != None:
            output_path = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"), "Personal")[0] + "\\" + "output.docx"
        else:
            output_path = os.path.join(pathf_, os.path.splitext(os.path.basename(path_))[0] + ".docx")
        doc.save(output_path)
    except PermissionError:
        tkinter.messagebox.showerror(f"权限错误：无法保存到路径 '{pathf_}'，请检查路径是否存在且有写入权限。")
    except Exception as e:
        tkinter.messagebox.showerror(f"保存文件时发生错误",e)
    finally:
        tkinter.messagebox.showinfo("OK","转换完成：已保存")
global win,cv
win = m.Tk(title="Markdown 转 Word")    
cv = m.Canvas(auto_zoom=True)
cv.place(width=1280, height=720)
m.Button(cv,(20,20),text="选择Markdown文件", command=selectPath)
if pyperclip.paste():
    con = pyperclip.paste()
    m.Text(cv,(280,25),text="已获取剪切板内容，自动使用剪贴板内容进行转换，自动保存在文档文件夹，文件名为output.docx")
else:
    con = None
    m.Text(cv,(20,60),text="未获取剪切板内容，请手动选择Markdown文件进行转换")
m.Button(cv,(20,60),text="选择Docx文件保存目录", command=selectFloder)
m.Text(cv,(280,65),text="可不选，默认为和原文件同目录")
m.Button(cv,(20,100),text="开始转换", command=covert)
win.mainloop()