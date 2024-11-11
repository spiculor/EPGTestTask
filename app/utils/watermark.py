import os
from PIL import Image
from io import BytesIO

async def add_watermark(image_data: bytes, watermark_path: str, output_path: str) -> None:

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with Image.open(BytesIO(image_data)) as base_image, Image.open(watermark_path) as watermark:
        watermark_ratio = base_image.width * 0.1 / watermark.width
        watermark = watermark.resize(
            (int(watermark.width * watermark_ratio), int(watermark.height * watermark_ratio))
        )

        position = (base_image.width - watermark.width, base_image.height - watermark.height)
        
        transparent = Image.new('RGBA', base_image.size)
        transparent.paste(base_image.convert('RGBA'), (0, 0))
        
        if watermark.mode != 'RGBA':
            watermark = watermark.convert('RGBA')
        
        transparent.paste(watermark, position, mask=watermark)
        
        output = BytesIO()
        transparent.convert('RGB').save(output, format="JPEG")
        with open(output_path, "wb") as f:
            f.write(output.getvalue())
