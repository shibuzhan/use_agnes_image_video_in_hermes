> ## Documentation Index
> Fetch the complete documentation index at: https://wiki.agnes-ai.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Agnes Video V2.0

> Agnes-Video-V2.0 API 接入指南

## 概述

Agnes-Video-V2.0 是一款面向生产场景的视频生成模型，支持**文生视频**、**图生视频**、**多图视频生成**以及**关键帧动画**工作流。

开发者可以使用文本提示词、图片 URL 或多张参考图片生成高质量视频。该模型适用于故事讲述、营销视频、产品演示、社交媒体内容、应用动态素材以及 AI 创意工作流。

<Info>
  Agnes-Video-V2.0 采用基于异步任务的 API。您需要先创建一个视频生成任务，然后使用返回的 `video_id` 或 `task_id` 获取视频结果。
</Info>

## 支持能力

<CardGroup cols={2}>
  <Card title="文生视频" icon="clapperboard">
    通过文本提示词直接生成视频
  </Card>

  <Card title="图生视频" icon="image">
    将静态图片转化为动态视频
  </Card>

  <Card title="多图视频生成" icon="layer-group">
    使用多张参考图片引导视频生成
  </Card>

  <Card title="关键帧动画" icon="timeline">
    在多个关键帧之间生成流畅过渡
  </Card>

  <Card title="场景运动控制" icon="camera">
    通过提示词控制主体动作、镜头运动和场景动态
  </Card>

  <Card title="视觉一致性" icon="eye">
    在帧间保持一致的主体、风格和场景
  </Card>

  <Card title="电影级输出" icon="film">
    生成高质量电影级视频
  </Card>

  <Card title="异步API" icon="clock">
    先提交任务，再获取生成结果
  </Card>
</CardGroup>

## 使用场景

<CardGroup cols={2}>
  <Card title="故事讲述" icon="book-open">
    短片、角色场景、叙事片段
  </Card>

  <Card title="营销视频" icon="bullhorn">
    产品广告、宣传视频、推广内容
  </Card>

  <Card title="社交媒体内容" icon="share-nodes">
    Reels、Shorts、TikTok 风格视频
  </Card>

  <Card title="图片动画" icon="wand-magic-sparkles">
    为肖像、产品、角色或场景添加动画效果
  </Card>

  <Card title="产品演示" icon="box">
    通过文本或图片生成产品展示视频
  </Card>

  <Card title="关键帧过渡" icon="arrows-left-right">
    在不同视觉状态之间生成流畅过渡
  </Card>

  <Card title="游戏/应用素材" icon="gamepad">
    为数字产品生成动态视觉素材
  </Card>

  <Card title="沉浸式内容" icon="vr-cardboard">
    生成电影级 AI 场景和氛围视频
  </Card>
</CardGroup>

## 前提条件

<Note>
  在接入之前，请确保您已满足以下条件：

  1. 拥有有效的 Agnes AI API Key。
  2. 具备访问 Agnes AI API 网关的网络条件。
  3. 确认模型名称：<code>agnes-video-v2.0</code>。
  4. 准备好用于视频生成的文本提示词。
  5. 如果使用图生视频、多图视频或关键帧动画功能，需要提供可公开访问的图片 URL。
</Note>

## API 接口

### 创建视频任务

| 项目         | 说明                                                         |
| ------------ | ------------------------------------------------------------ |
| 接口地址     | [https://apihub.agnes-ai.com/v1/videos](https://apihub.agnes-ai.com/v1/videos) |
| 请求方法     | POST                                                         |
| Content-Type | application/json                                             |
| 认证方式     | Bearer Token                                                 |
| 请求头       | Authorization: Bearer YOUR\_API\_KEY                         |

### 获取视频结果：推荐方式

视频任务创建成功后，响应中会包含一个 `video_id`。

推荐使用 `video_id` 来获取视频结果。

| 项目     | 说明                                                       |
| -------- | ---------------------------------------------------------- |
| 接口地址 | `https://apihub.agnes-ai.com/agnesapi?video_id=<VIDEO_ID>` |
| 请求方法 | GET                                                        |
| 认证方式 | Bearer Token                                               |
| 请求头   | Authorization: Bearer YOUR\_API\_KEY                       |

### 获取视频结果：兼容旧版方式

为了兼容现有集成，旧版任务查询接口仍然支持使用。

| 项目     | 说明                                                         |
| -------- | ------------------------------------------------------------ |
| 接口地址 | [https://apihub.agnes-ai.com/v1/videos/\{task\_id}](https://apihub.agnes-ai.com/v1/videos/\{task_id}) |
| 请求方法 | GET                                                          |
| 认证方式 | Bearer Token                                                 |
| 请求头   | Authorization: Bearer YOUR\_API\_KEY                         |

## 请求参数

### 创建视频任务参数

| 参数                  | 类型           | 必填 | 说明                                      |
| --------------------- | -------------- | ---- | ----------------------------------------- |
| model                 | string         | 是   | 模型名称。使用 agnes-video-v2.0           |
| prompt                | string         | 是   | 视频内容的文本描述                        |
| image                 | string / array | 否   | 图片 URL 或图片 URL 数组                  |
| mode                  | string         | 否   | 生成模式，例如 ti2vid 或 keyframes        |
| height                | integer        | 否   | 视频高度。默认值：768                     |
| width                 | integer        | 否   | 视频宽度。默认值：1152                    |
| num\_frames           | integer        | 否   | 视频帧数。必须 ≤ 441 且遵循 8n + 1 规则   |
| frame\_rate           | number         | 否   | 视频帧率。支持范围：1–60                  |
| num\_inference\_steps | integer        | 否   | 推理步数                                  |
| seed                  | integer        | 否   | 随机种子，用于生成可复现的结果            |
| negative\_prompt      | string         | 否   | 反向提示词，描述需要避免的内容            |
| extra\_body.image     | array          | 否   | 多图视频或关键帧模式下的输入图片 URL 数组 |
| extra\_body.mode      | string         | 否   | 附加模式设置，例如 keyframes              |

### 参数标准化

Agnes-Video-V2.0 会对部分视频生成参数进行标准化处理，以确保生成稳定性和输出质量的一致性。当提交的 `width`、`height` 或宽高比与模型支持的标准规格不完全匹配时，系统会自动识别最接近的分辨率档位和宽高比，并将请求映射到对应的标准输出尺寸。

模型目前支持三个标准分辨率档位：`480p`、`720p` 和 `1080p`。推荐使用以下宽高比：

| 宽高比 | 推荐使用场景                                                 |
| ------ | ------------------------------------------------------------ |
| 16:9   | 横版视频、产品演示、网站展示、YouTube 风格内容               |
| 9:16   | 竖版短视频、移动端优先内容、TikTok / Reels / Shorts 风格内容 |
| 1:1    | 方形视频、社交媒体信息流、角色或产品展示                     |
| 4:3    | 传统横版格式及通用演示内容                                   |
| 3:4    | 竖版演示、以肖像为主的视频、以产品为主的内容                 |

不同分辨率与宽高比的组合可能对应不同的实际输出尺寸和最大帧数限制。例如，接近 `720p / 16:9` 的输入尺寸将被标准化为对应的标准输出尺寸。

因此，请求中原始的 `width`、`height`、`num_frames` 等参数可能与生成时使用的标准化参数不完全一致。在展示任务信息、计算视频时长或排查生成结果问题时，开发者应以 API 响应中返回的 `size`、`seconds` 等字段为准。

## 创建视频任务

<Tabs>
  <Tab title="示例 1：文生视频">
    使用此请求通过文本提示词直接生成视频。

    ```bash theme={null}
    curl -X POST https://apihub.agnes-ai.com/v1/videos \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "agnes-video-v2.0",
        "prompt": "A cinematic shot of a cat walking on the beach at sunset, soft ocean waves, warm golden lighting, realistic motion",
        "height": 768,
        "width": 1152,
        "num_frames": 121,
        "frame_rate": 24
      }'
    ```
  </Tab>

  <Tab title="示例 2：图生视频">
    使用此请求为单张图片添加动画效果。

    ```bash theme={null}
    curl -X POST https://apihub.agnes-ai.com/v1/videos \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "agnes-video-v2.0",
        "prompt": "The woman slowly turns around and looks back at the camera, natural facial expression, cinematic camera movement",
        "image": "https://example.com/image.png",
        "num_frames": 121,
        "frame_rate": 24
      }'
    ```
  </Tab>

  <Tab title="示例 3：多图视频生成">
    使用此请求通过多张输入图片引导视频生成。

    ```bash theme={null}
    curl -X POST https://apihub.agnes-ai.com/v1/videos \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "agnes-video-v2.0",
        "prompt": "Create a smooth transformation scene between the two reference images, cinematic lighting, consistent character identity, natural motion",
        "extra_body": {
          "image": [
            "https://example.com/image1.png",
            "https://example.com/image2.png"
          ]
        },
        "num_frames": 121,
        "frame_rate": 24
      }'
    ```
  </Tab>

  <Tab title="示例 4：关键帧动画">
    使用此请求在多个关键帧之间生成流畅动画。

    ```bash theme={null}
    curl -X POST https://apihub.agnes-ai.com/v1/videos \
      -H "Authorization: Bearer YOUR_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "agnes-video-v2.0",
        "prompt": "Generate a smooth cinematic transition between the keyframes, maintaining visual consistency and natural camera movement",
        "extra_body": {
          "image": [
            "https://example.com/keyframe1.png",
            "https://example.com/keyframe2.png"
          ],
          "mode": "keyframes"
        },
        "num_frames": 121,
        "frame_rate": 24
      }'
    ```
  </Tab>
</Tabs>

## 创建任务响应

视频任务创建成功后，API 会返回任务信息。

响应中同时包含 `task_id` 和 `video_id`。

`video_id` 是获取视频结果的推荐 ID。

```json theme={null}
{
  "id": "task_YOUR_TASK_ID",
  "task_id": "task_YOUR_TASK_ID",
  "video_id": "video_YOUR_VIDEO_ID",
  "object": "video",
  "model": "agnes-video-v2.0",
  "status": "queued",
  "progress": 0,
  "created_at": 1780457477,
  "seconds": "10.0",
  "size": "1280x768"
}
```

### 响应字段

| 字段        | 类型    | 说明                              |
| ----------- | ------- | --------------------------------- |
| id          | string  | 任务 ID。可与旧版查询接口配合使用 |
| task\_id    | string  | 任务 ID。作用与 id 相同           |
| video\_id   | string  | 视频 ID。推荐用于获取视频结果     |
| object      | string  | 对象类型，通常为 video            |
| model       | string  | 当前任务使用的模型                |
| status      | string  | 当前任务状态                      |
| progress    | integer | 当前任务进度百分比                |
| created\_at | integer | 任务创建时间戳                    |
| seconds     | string  | 视频时长（秒）                    |
| size        | string  | 视频分辨率                        |

## 获取视频结果

### 推荐方式：通过 `video_id` 获取

创建视频任务后，使用返回的 `video_id` 来获取视频结果。

```bash theme={null}
curl --location --request GET 'https://apihub.agnes-ai.com/agnesapi?video_id=<VIDEO_ID>' \
  --header 'Authorization: Bearer <API_KEY>'
```

示例：

```bash theme={null}
curl --location --request GET 'https://apihub.agnes-ai.com/agnesapi?video_id=video_xxxxxx' \
  --header 'Authorization: Bearer <API_KEY>'
```

### 可选参数：`model_name`

获取视频结果时，您还可以传入 `model_name` 来显式指定模型名称。

```bash theme={null}
curl --location --request GET 'https://apihub.agnes-ai.com/agnesapi?video_id=<VIDEO_ID>&model_name=<MODEL>' \
  --header 'Authorization: Bearer <API_KEY>'
```

示例：

```bash theme={null}
curl --location --request GET 'https://apihub.agnes-ai.com/agnesapi?video_id=video_xxxxxx&model_name=agnes-video-v2.0' \
  --header 'Authorization: Bearer <API_KEY>'
```

在以下情况下使用 `model_name`：

1. 您使用的是上游原始视频 ID。
2. 使用的模型不是默认模型 `agnes-video-v2.0`。
3. 您希望显式指定获取结果所使用的模型。

当提供 `model_name` 时，该参数将优先生效。

### 兼容旧版方式：通过 `task_id` 获取

为兼容旧版本，您仍然可以使用 `task_id` 获取视频结果。

```bash theme={null}
curl --location --request GET 'https://apihub.agnes-ai.com/v1/videos/<TASK_ID>' \
  --header 'Authorization: Bearer <API_KEY>'
```

示例：

```bash theme={null}
curl --location --request GET 'https://apihub.agnes-ai.com/v1/videos/task_xxxxxx' \
  --header 'Authorization: Bearer <API_KEY>'
```

此方式仍然支持，但新接入的集成应使用 `video_id` 获取方式。

## 获取结果响应

任务完成后，API 返回最终视频结果。

```json theme={null}
{
  "id": "task_YOUR_TASK_ID",
  "video_id": "video_YOUR_VIDEO_ID",
  "model": "agnes-video-v2.0",
  "object": "video",
  "status": "completed",
  "progress": 100,
  "seconds": "10.0",
  "size": "1280x768",
  "remixed_from_video_id": "https://storage.googleapis.com/agnes-aigc/aigc/videos/2026/06/03/video_xxxxxx.mp4",
  "error": null
}
```

### 结果字段

| 字段                     | 类型          | 说明                                                |
| ------------------------ | ------------- | --------------------------------------------------- |
| id                       | string        | 任务 ID                                             |
| video\_id                | string        | 视频 ID                                             |
| model                    | string        | 当前任务使用的模型                                  |
| object                   | string        | 对象类型                                            |
| status                   | string        | 任务状态                                            |
| progress                 | integer       | 任务进度百分比                                      |
| seconds                  | string        | 视频时长（秒）                                      |
| size                     | string        | 视频分辨率                                          |
| remixed\_from\_video\_id | string        | 最终生成的视频 URL。仅在 status 为 completed 时可用 |
| error                    | object / null | 任务失败时返回的错误信息                            |

## 任务状态

| 状态         | 说明               |
| ------------ | ------------------ |
| queued       | 任务正在队列中等待 |
| in\_progress | 视频正在生成       |
| completed    | 视频生成成功       |
| failed       | 视频生成失败       |

## 视频时长控制

Agnes-Video-V2.0 支持通过 `num_frames` 和 `frame_rate` 控制视频时长。

计算公式：

```text theme={null}
seconds = num_frames / frame_rate
```

其中：

* `num_frames` 是生成视频的总帧数；
* `frame_rate` 是视频帧率，即每秒播放的帧数；
* `num_frames` 必须小于或等于 `441`；
* `num_frames` 必须遵循 `8n + 1` 规则；
* `frame_rate` 支持 `1` 到 `60` 之间的值。

### 常用时长设置

| 目标时长 | 推荐参数                          |
| -------- | --------------------------------- |
| 约 3 秒  | num\_frames: 81, frame\_rate: 24  |
| 约 5 秒  | num\_frames: 121, frame\_rate: 24 |
| 约 10 秒 | num\_frames: 241, frame\_rate: 24 |
| 约 18 秒 | num\_frames: 441, frame\_rate: 24 |

要生成更长的视频，可以增大 `num_frames` 或降低 `frame_rate`。

要使运动更加流畅，请使用更高的 `frame_rate`，例如 `24` 或 `30`。但在相同的 `num_frames` 下，更高的 `frame_rate` 会导致视频时长更短。

## 推荐参数

| 场景             | 推荐设置                                                    |
| ---------------- | ----------------------------------------------------------- |
| 标准视频生成     | width: 1152, height: 768, num\_frames: 121, frame\_rate: 24 |
| 社交短视频       | num\_frames: 81 或 121, frame\_rate: 24                     |
| 较长视频         | 增大 num\_frames 或降低 frame\_rate                         |
| 更流畅的运动     | 使用 frame\_rate: 24 或 30                                  |
| 可复现结果       | 设置固定的 seed                                             |
| 关键帧过渡       | 使用 extra\_body.mode: "keyframes"                          |
| 避免不需要的内容 | 使用 negative\_prompt                                       |

## 提示词最佳实践

<AccordionGroup>
  <Accordion title="文生视频提示词">
    对于文生视频任务，建议描述主体、动作、场景、镜头运动、光线和视觉风格。

    推荐结构：
    
    ```text theme={null}
    [主体] + [动作] + [场景] + [镜头运动] + [光线] + [风格]
    ```
    
    示例：
    
    ```text theme={null}
    A young astronaut walking across a red desert planet, dust blowing in the wind, slow cinematic tracking shot, dramatic sunset lighting, realistic sci-fi style
    ```
  </Accordion>

  <Accordion title="图生视频提示词">
    对于图生视频任务，描述哪些内容应该运动，以及哪些关键主体元素应该保持稳定。

    示例：
    
    ```text theme={null}
    Animate the character with subtle breathing motion, hair moving gently in the wind, background lights flickering softly, while keeping the face and outfit consistent
    ```
  </Accordion>

  <Accordion title="多图视频提示词">
    对于多图视频任务，描述输入图片之间的关系以及场景应该如何过渡。

    示例：
    
    ```text theme={null}
    Use the first image as the starting scene and the second image as the target scene. Create a smooth transformation with consistent lighting, natural motion, and cinematic pacing
    ```
  </Accordion>

  <Accordion title="关键帧动画提示词">
    对于关键帧动画任务，清晰描述关键帧之间的过渡关系。

    示例：
    
    ```text theme={null}
    Create a smooth transition from the first keyframe to the second keyframe, maintaining character identity, consistent camera angle, and natural motion between scenes
    ```
  </Accordion>
</AccordionGroup>

## 错误码

| 状态码 | 说明                       |
| ------ | -------------------------- |
| 400    | 请求无效。请检查请求参数   |
| 401    | 未授权。请检查您的 API Key |
| 404    | 任务或视频未找到           |
| 500    | 服务器错误                 |
| 503    | 服务繁忙。请稍后重试       |

## 定价

| 类型     | 标准价格     | 当前价格 |
| -------- | ------------ | -------- |
| 视频时长 | \$0.005 / 秒 | \$0 / 秒 |

## 注意事项

<Check>
  * 使用 `agnes-video-v2.0` 作为模型名称。
  * 视频生成是异步的。
  * 您需要先创建视频任务，然后获取视频结果。
  * 创建任务响应会同时返回 `task_id` 和 `video_id`。
  * 新接入的集成应使用 `video_id` 获取视频结果。
  * 旧版 `task_id` 查询接口仍然支持。
  * `video_url` 仅在 `status` 为 `completed` 时可用。
  * `num_frames` 必须小于或等于 `441`。
  * `num_frames` 必须遵循 `8n + 1` 规则，例如 `81`、`121`、`161`、`241` 或 `441`。
  * 文生视频任务仅需要 `model` 和 `prompt`。
  * 图生视频任务需要通过 `image` 传入图片 URL。
  * 多图视频任务需要在 `extra_body.image` 中传入多个图片 URL。
  * 关键帧动画需要将 `extra_body.mode` 设置为 `keyframes`。
</Check>