# pic_to_wall
USTB小作业，利用爬虫获取的照片组合成一定的图案，本文以组合成一定的字符为例。
> PIL(Python Image Library)是python的第三方图像处理库，但是由于其强大的功能与众多的使用人数，几乎已经被认为是python官方图像处理库了。其官方主页为:[PIL](http://pythonware.com/products/pil/)。 PIL历史悠久，原来是只支持python2.x的版本的，后来出现了移植到python3的库[pillow](http://python-pillow.org/),pillow号称是`friendly fork for PIL`,其功能和PIL差不多，但是支持python3。本文只使用了PIL那些最常用的特性与用法,主要参考自:[http://www.effbot.org/imagingbook](http://www.effbot.org/imagingbook)。

# Part 1:利用python生成照片墙
## （1）简要介绍思路：
（1）通过给定字符串生成一张图片；
（2）然后将该图片的每个像素的宽扩张edge_len倍，高也扩张edge_len倍，假设edge_len=60，那么原文字图片的每个像素就变成了60*60像素的一个图片；
（3）原文字图片的每个像素的透明度不同，显示文字的地方，透明度低（不透明），这2个字周边的地方，透明度高（透明），我们根据原文字图片每个像素的透明度，来设定放到这个像素（其实宽高已经扩大了60倍）图片的透明度（trans_alpha方法实现）。

## （2）导入库文件
```javascript
from PIL import Image, ImageDraw, ImageFont
import os
```
## （3）由文字生成图像
```javascript
def gen_text_img(text, font_size=20, font_path=None):
    # args：文字内容，文字字体大小，字体路径
    font = ImageFont.truetype(font_path, font_size) if font_path is not None else None
    (width, length) = font.getsize(text)  # 获取文字大小
    text_img = Image.new('RGBA', (width, length))
    draw = ImageDraw.Draw(text_img)
    # 第一个tuple表示未知(left,up)，之后是文字，然后颜色，最后设置字体
    draw.text((0, 0), text, fill=(0, 0, 0), font=font)
    text_img.save('./temp_pic.png')
    return text_img
```
## （4）透明度调节
```javascript
def trans_alpha(img, pixel):
    '''
    根据rgba的pixel调节img的透明度
    这里传进来的pixel是一个四元组（r,g,b,alpha）
    '''
    _, _, _, alpha = img.split()
    alpha = alpha.point(lambda i: pixel[-1]*10)
    img.putalpha(alpha)   #Part2有介绍
    return img
```
## （5）根据透明度参数对放大文字图进行像素覆盖
```javascript
def picture_wall_mask(text_img, edge_len, pic_dir="./user"):
    # 根据文字图gen_text_img像生成对应的照片墙，输入：文字图像，各个照片边长，照片所在路径
    new_img = Image.new('RGBA', (text_img.size[0] * edge_len, text_img.size[1] * edge_len))
    file_list = os.listdir(pic_dir)
    img_index = 0
    for x in range(0, text_img.size[0]):
        for y in range(0, text_img.size[1]):
            pixel = text_img.getpixel((x, y))#Part2有介绍
            file_name = file_list[img_index % len(file_list)]
            try:
                img = Image.open(os.path.join(pic_dir, file_name)).convert('RGBA')#Part2有介绍
                img = img.resize((edge_len, edge_len))
                img = trans_alpha(img, pixel)
                new_img.paste(img, (x * edge_len, y * edge_len)) #指定区域替换，Part2有介绍
                img_index += 1
            except Exception as e:
                print(f"open file {file_name} failed! {e}")
    return new_img
```
## （6）生成照片墙
```javascript
def main(text='', font_size = 20, edge_len = 60,pic_dir = "./user", out_dir = "./out/", font_path = './demo.ttf'):
    '''
    生成照片墙
    :param text: Text of picture wall, if not defined this will generage a rectangle picture wall
    :param font_size: font size of a clear value
    :param edge_len: sub picture's egde length
    '''
    if len(text) >= 1:
        text_ = ' '.join(text)#将字符串用空格分隔开，提高展示效果
        #text_ = text
        print(f"generate text wall for '{text_}' with picture path:{pic_dir}")
        text_img = gen_text_img(text_, font_size, font_path)
        # text_img.show()
        img_ascii = picture_wall_mask(text_img, edge_len, pic_dir)
        # img_ascii.show()
        img_ascii.save(out_dir + os.path.sep + '_'.join(text) + '.png')
```
## （7）函数执行与传参
```javascript
if __name__ == '__main__':
    main(text='python')
```
文件目录结构如下，以供参考：out存放生成的照片墙，user存放贴上去的图片。
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200405150550720.png)
# Part 2:图像处理过程中中学习到的几个知识点：
## （1）python PNG图片显示
### 导入库文件
> 仅适用于显示png格式的图片
```javascript
import matplotlib.pyplot as plt # plt 用于显示图片
import matplotlib.image as mpimg # mpimg 用于读取图片

```
### 显示图片
```javascript
lena = mpimg.imread('temp_pic.png') # 读取和代码处于同一目录下的 lena.png
# 此时 lena 就已经是一个 np.array 了，可以对它进行任意处理
lena.shape #(512, 512, 3)
plt.imshow(lena) # 显示图片
plt.axis('off') # 不显示坐标轴
plt.show()
```
## （2）PIL中图像格式转换img.convert()函数
> 在数字图像处理中，针对不同的图像格式有其特定的处理算法。所以，在做图像处理之前，我们需要考虑清楚自己要基于哪种格式的图像进行算法设计及其实现。本文基于这个需求，使用python中的图像处理库PIL来实现不同图像格式的转换。
对于彩色图像，不管其图像格式是PNG，还是BMP，或者JPG，在PIL中，使用Image模块的open()函数打开后，返回的图像对象的模式都是“RGB”。而对于灰度图像，不管其图像格式是PNG，还是BMP，或者JPG，打开后，其模式为“L”。对于PNG、BMP和JPG彩色图像格式之间的互相转换都可以通过Image模块的open()和save()函数来完成。具体说就是，在打开这些图像时，PIL会将它们解码为三通道的“RGB”图像。用户可以基于这个“RGB”图像，对其进行处理。处理完毕，使用函数save()，可以将处理结果保存成PNG、BMP和JPG中任何格式。这样也就完成了几种格式之间的转换。同理，其他格式的彩色图像也可以通过这种方式完成转换。当然，对于不同格式的灰度图像，也可通过类似途径完成，只是PIL解码后是模式为“L”的图像。

而对于Part 1中convert()函数的使用，推荐一篇博文[Python图像处理库PIL中图像格式转换](https://blog.csdn.net/icamera0/article/details/50843172)以供参考学习。
## （3）img.paste()函数
第一个参数是用来覆盖的图片，第二个参数是覆盖的位置,[参考博文](https://blog.csdn.net/weixin_41396062/article/details/84037428)。
## （4）img.getpixel()函数
查看图像存储值，[参考博文](https://blog.csdn.net/MiniCatTwo/article/details/80608076)。
## （5）python图像处理：给图像添加透明度（alpha通道）
主要介绍img.putalpha()函数的用法，[参考博文](https://blog.csdn.net/guduruyu/article/details/71440186)
