from zhipuai import ZhipuAI
import requests
import base64
import mimetypes

def get_minio_image_as_base64(minio_url: str) -> str:
    """
    从MinIO获取图片并转换为base64编码
    GLM-4.6v支持data URL格式: data:image/png;base64,xxxxx
    """
    try:
        response = requests.get(minio_url)
        response.raise_for_status()

        # 编码为base64
        image_base64 = base64.b64encode(response.content).decode('utf-8')

        print(f"图片大小: {len(response.content)} bytes")
        print(f"Base64长度: {len(image_base64)}")

        # 返回data URL格式: data:image/png;base64,xxxxx
        return f"data:image/png;base64,{image_base64}"
    except Exception as e:
        print(f"获取图片失败: {e}")
        return None

def analyze_image_with_minio_url(minio_url: str, prompt: str = "这张图片讲的是什么？"):
    """
    使用视觉大模型分析MinIO中的图片
    """
    # 将MinIO URL转换为base64编码
    image_base64 = get_minio_image_as_base64(minio_url)

    if image_base64 is None:
        print("无法获取图片")
        return

    client = ZhipuAI(api_key="86d71d785fa041ab8d57e3cd4c826d3b.mqKgFRhLQqoiXoEy")

    response = client.chat.completions.create(
        model="glm-4.6v",
        messages=[
            {
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_base64  # 使用纯base64编码的图片
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ],
                "role": "user"
            }
        ],
        thinking={
            "type":"enabled"
        }
    )
    print(response.choices[0].message)
    return response.choices[0].message

# 使用示例
if __name__ == "__main__":
    # 测试MinIO本地URL
    minio_url = "http://localhost:9000/pdf-images/doc2.pdf/doc2.pdf_page1_img1_4724cc06.png"
    # 使用MinIO URL（自动转换为base64）
    print("=== 使用MinIO URL分析图片 ===")
    analyze_image_with_minio_url(minio_url)


# import requests

# url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# payload = {
#     "model": "glm-4.6v",
#     "messages": [
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "image_url",
#                     "image_url": { "url": "https://cloudcovert-1305175928.cos.ap-guangzhou.myqcloud.com/%E5%9B%BE%E7%89%87grounding.PNG" }
#                 },
#                 {
#                     "type": "text",
#                     "text": "这些图片讲的是什么？"
#                 }
#             ]
#         }
#     ]
# }
# headers = {
#     "Authorization": "Bearer <token>",
#     "Content-Type": "application/json"
# }

# response = requests.post(url, json=payload, headers=headers)

# print(response.text)