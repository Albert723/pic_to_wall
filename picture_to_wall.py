#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:Yihao Wu

from PIL import Image, ImageDraw, ImageFont
import os

def gen_text_img(text, font_size=20, font_path=None):
    # 从文字生成图像，输入：文字内容，文字字体大小，字体路径
    font = ImageFont.truetype(font_path, font_size) if font_path is not None else None
    (width, length) = font.getsize(text)  # 获取文字大小
    text_img = Image.new('RGBA', (width, length))
    draw = ImageDraw.Draw(text_img)
    # 第一个tuple表示未知(left,up)，之后是文字，然后颜色，最后设置字体
    draw.text((0, 0), text, fill=(0, 0, 0), font=font)
    text_img.save('./temp_pic.png')
    return text_img

def trans_alpha(img, pixel):
    '''
    根据rgba的pixel调节img的透明度
    这里传进来的pixel是一个四元组（r,g,b,alpha）
    '''
    _, _, _, alpha = img.split()
    alpha = alpha.point(lambda i: pixel[-1]*10)
    img.putalpha(alpha)
    return img

def picture_wall_mask(text_img, edge_len, pic_dir="./user"):
    # 根据文字图gen_text_img像生成对应的照片墙，输入：文字图像，各个照片边长，照片所在路径
    new_img = Image.new('RGBA', (text_img.size[0] * edge_len, text_img.size[1] * edge_len))
    file_list = os.listdir(pic_dir)
    img_index = 0
    for x in range(0, text_img.size[0]):
        for y in range(0, text_img.size[1]):
            pixel = text_img.getpixel((x, y))
            file_name = file_list[img_index % len(file_list)]
            try:
                img = Image.open(os.path.join(pic_dir, file_name)).convert('RGBA')
                img = img.resize((edge_len, edge_len))
                img = trans_alpha(img, pixel)
                new_img.paste(img, (x * edge_len, y * edge_len))
                img_index += 1
            except Exception as e:
                print(f"open file {file_name} failed! {e}")
    return new_img

def main(text='', font_size = 20, edge_len = 180,pic_dir = "./user", out_dir = "./out/", font_path = './demo.ttf'):
    '''
    生成照片墙
    :param text: Text of picture wall, if not defined this will generage a rectangle picture wall
    :param font_size: font size of a clear value
    :param edge_len: sub picture's egde length
    '''
    if len(text) >= 1:
        text_ = ' '.join(text)#将字符串用空格分隔开
        #text_ = text
        print(f"generate text wall for '{text_}' with picture path:{pic_dir}")
        text_img = gen_text_img(text_, font_size, font_path)
        # text_img.show()
        img_ascii = picture_wall_mask(text_img, edge_len, pic_dir)
        # img_ascii.show()
        img_ascii.save(out_dir + os.path.sep + '_'.join(text) + '.png')

if __name__ == '__main__':
    main(text='医者仁心')
