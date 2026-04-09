# 项目使用python语言作为服务端,静态html作为前端
# 项目实现步骤
## 1 服务端创建接口: 服务器状态检查
1. 收到前端的请求后,会使用get方法请求DrawThings服务地址(默认http://127.0.0.1:7888,可由前端配置,不需要用户填写**http://**自动补充), 如果成功返回,则提示检测成功. drawThings的服务返回的json结构如下:
```json
{"strength":1,"controls":[],"clip_l_text":null,"tea_cache_end":-1,"causal_inference_pad":0,"sampler":"UniPC Trailing","stochastic_sampling_gamma":0.3,"mask_blur":1.5,"batch_size":1,"original_width":768,"image_prior_steps":5,"aesthetic_score":6,"target_height":768,"upscaler_scale":0,"stage_2_shift":1,"fps":5,"model":"z_image_turbo_1.0_q6p.ckpt","negative_aesthetic_score":2.5,"zero_negative_prompt":false,"negative_original_height":512,"shift":3,"diffusion_tile_height":1024,"cfg_zero_star":false,"cfg_zero_init_steps":0,"clip_weight":1,"seed_mode":"Scale Alike","diffusion_tile_overlap":128,"upscaler":"realesrgan_x2plus_f16.ckpt","guidance_embed":3.5,"separate_clip_l":false,"start_frame_guidance":1,"mask_blur_outset":0,"t5_text_encoder_decoding":true,"steps":8,"negative_prompt_for_image_prior":true,"hires_fix_strength":0.699999988079071,"resolution_dependent_shift":false,"tea_cache_max_skip_steps":3,"separate_t5":false,"compression_artifacts":"disabled","refiner_model":null,"preserve_original_after_inpaint":true,"causal_inference":0,"sharpness":0,"image_guidance":1.5,"motion_scale":127,"target_width":768,"t5_text":null,"guidance_scale":1,"crop_left":0,"original_height":768,"width":768,"tiled_diffusion":false,"tea_cache":false,"open_clip_g_text":null,"speed_up_with_guidance_embed":true,"crop_top":0,"batch_count":1,"tea_cache_threshold":0.20000000298023224,"compression_artifacts_quality":43.099998474121094,"decoding_tile_width":640,"negative_original_width":512,"negative_prompt":"ugly, deformed, disfigured, bad anatomy, extra limbs, missing limbs, floating limbs, mutated hands, poorly drawn hands, poorly drawn face, mutation, blurry, bad proportions, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck, watermark, text, signature, lowres, worst quality, low quality, normal quality, jpeg artifacts, out of frame, cropped","stage_2_guidance":1,"loras":[{"mode":"all","file":"z_image_turbo_fun_control...(truncated)
```
2. 将返回结果中的当前提示词(prompt),以及模型(model)返回到前端, 让前端显示
## 2 编写前端页面
 1. 创建静态html页面,一进页面就请求python后端接口**服务器状态检查**, 如果状态检查成功, 显示当前的"提示词"和"模型".
 2. 状态检查失败时,弹出配置输入框让用户设置DrawThings服务的IP和端口(默认http://127.0.0.1:7888),用户保存后重新检测
 3. 如果检查成功,则显示表单,有以下字段:
    - 提示词**prompt**
    - 图片尺寸下拉选择框,预设几个比例的尺寸,字段分别为**width** 和 **height**
    - **seed**(默认为-1)
    - 负面提示词(默认折叠起来),默认值ugly, deformed, disfigured, bad anatomy, extra limbs, missing limbs, floating limbs, mutated hands, poorly drawn hands, poorly drawn face, mutation, blurry, bad proportions, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck, watermark, text, signature, lowres, worst quality, low quality, normal quality, jpeg artifacts, out of frame, cropped
    - 步数**steps**
    - 生成按钮, 点击生成会想python服务端请求**生成**接口
4. 经过一段时间后, python后端会返回生成结果,包含以下内容:
    - 生成的图片,支持放大\缩小\保存
    - 生成图片耗时,以及seed值
5. 用户填写过的字段会保存到浏览器的本地储存,下次打开会默认填上
6. 生成结果的页面有一个返回页面,可以再次执行生成的操作.
## 3 服务端接受前端**生成**请求
1. 接受前端的参数和DrawThings服务地址,通过post请求转发至**{ip}:{port}/sdapi/v1/txt2img**, 这个接口耗时较长,预计需要5分钟左右.请求之后就开始计时.
2. 请求成功后会返回json数据,其中data值是图片的base64编码的值,需要把图片临时保存在当前文件夹
3. 计时结束,保存耗时,每次请求都保存耗时,计算一个平均耗时.
4. 再次请求**{ip}:{port}**获取seed值
5. 将图片,平均耗时,seed值返回到前端
