import qrcode
from PIL import Image

def create_qrcode(url: str, icon_path: str) -> None:
    # 1. 生成二维码
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    # 2. 打开 logo
    icon = Image.open(icon_path).convert("RGBA")

    # 3. 计算 logo 尺寸（二维码 1/4）
    w, h = img.size
    icon_w = icon_h = min(w, h) // 4
    icon = icon.resize((icon_w, icon_h), Image.LANCZOS)

    # 4. 透明边框
    new_img = Image.new("RGBA", (icon_w + 8, icon_h + 8), (255, 255, 255, 0))
    new_img.paste(icon, (4, 4), icon)

    # 5. 贴到二维码中心
    pos = ((w - icon_w) // 2, (h - icon_h) // 2)
    img.paste(new_img, pos, new_img)

    # 6. 保存
    img.save("qr.png", quality=100)
    print("qr.png 已生成")

if __name__ == '__main__':
    create_qrcode("http://python3web.com", "logo.png")