# 图生图提示词原则

## 核心原则：极简提示词

Agnes Image 2.1 Flash 图生图（img2img）的提示词应极简短，**只写角色名 + 照片风格效果**。

```
✅ 正确: "Takanashi Rikka cosplay photo, dreamy haze, motion blur"
✅ 正确: "Hatsune Miku, cinematic lighting, shallow depth of field"
❌ 错误: "Change hair to long dark blue twin-tails with orange clips, change eyepatch from white to black..."
```

## 为什么？

- 详细描述角色外观 → 模型会忽略参考图，按文字"硬生成" → 结果与原图构图完全无关
- 简短提示词 → 模型从参考图提取构图、姿势、布局，只根据角色名和效果描述做变换

## 不要额外添加不存在的东西

- 参考图上没有的东西，提示词里不要写（如"add wings"）
- 模型会真的加上去，而原角色可能根本没有

## KEEP vs CHANGE

需要告诉模型保留什么、改变什么时，用最概括的语言：

```
✅ "Keep the pose and composition, change the character into Miku"
```

而非各种细节的枚举。
