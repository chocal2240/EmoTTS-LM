import customtkinter as ctk
import pygame
import threading
import time
import requests
import random
import math
import json
import os
from tkinter import messagebox, filedialog

CONFIG_FILE = "tts_config.json"

QWEN_EMOTIONS = [
    "平静支持 (soothing)",
    "温暖共情 (warm)",
    "冷静安抚 (calm)",
    "积极鼓励 (excited)",
    "庄重说明 (serious)",
    "探询引导 (inquisitive)",
]

PERSONA_PRESETS = {
    "心理咨询师": {
        "style": "empathetic",
        "speed": "slow",
        "temperature": 0.80,
        "top_p": 0.95,
        "openai_voice": "nova",
    },
    "温柔倾听者": {
        "style": "supportive",
        "speed": "slow",
        "temperature": 0.78,
        "top_p": 0.95,
        "openai_voice": "shimmer",
    },
    "理性分析师": {
        "style": "clear",
        "speed": "medium",
        "temperature": 0.72,
        "top_p": 0.90,
        "openai_voice": "alloy",
    },
    "成长教练": {
        "style": "encouraging",
        "speed": "medium",
        "temperature": 0.86,
        "top_p": 0.95,
        "openai_voice": "echo",
    },
}

LOCAL_ADAPTER_PRESETS = {
    "结项最终模型 (final_1500)": "/root/autodl-tmp/qwen3_tts_lora/deliverables/final_release_final_closure_20260323_001455/adapter",
    "情感快版新模型 (emotion_refine_fast)": "/root/autodl-tmp/qwen3_tts_lora/output_lora_emotion_refine_fast_e1/checkpoint-epoch-0/adapter",
    "离线提质新模型 (offline8h)": "/root/autodl-tmp/qwen3_tts_lora/deliverables/model_offline8h/adapter",
    "上一版 tri-mix": "/root/autodl-tmp/qwen3_tts_lora/output_lora_tri_mix_e1/checkpoint-epoch-0/adapter",
}
DEFAULT_LOCAL_ADAPTER = LOCAL_ADAPTER_PRESETS["结项最终模型 (final_1500)"]

EMOTION_PROFILES = {
    "soothing": {"top_p": 0.86, "temperature": 0.66, "speed": "slow"},
    "warm": {"top_p": 0.91, "temperature": 0.76, "speed": "slow"},
    "calm": {"top_p": 0.84, "temperature": 0.62, "speed": "slow"},
    "excited": {"top_p": 0.98, "temperature": 0.96, "speed": "medium"},
    "serious": {"top_p": 0.82, "temperature": 0.58, "speed": "medium"},
    "inquisitive": {"top_p": 0.93, "temperature": 0.88, "speed": "medium"},
}

PERSONA_REF_AUDIO = {
    "心理咨询师": "/root/autodl-tmp/dataset/Emotion Speech Dataset/0001/Neutral/0001_000001.wav",
    "温柔倾听者": "/root/autodl-tmp/dataset/Emotion Speech Dataset/0002/Neutral/0002_000001.wav",
    "理性分析师": "/root/autodl-tmp/dataset/Emotion Speech Dataset/0003/Neutral/0003_000001.wav",
    "成长教练": "/root/autodl-tmp/dataset/Emotion Speech Dataset/0004/Neutral/0004_000001.wav",
}

pygame.mixer.init()

class AdvancedTTSApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI 情感语音高级工作站")
        self.geometry("920x900")
        self.minsize(860, 820)
        
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.is_playing = False
        self.is_paused = False
        self.current_file = None
        self.volume = 0.8
        self.animation_id = None
        self.viz_mode = "wave"
        self.is_generating = False
        self.gen_start_time = None
        self.gen_timer_id = None
        self.audio_history = []
        self.history_display_values = []
        self.resize_job = None

        self.load_config()

        self.setup_ui()

    def setup_ui(self):
        self.title_label = ctk.CTkLabel(self, text="AI 情感语音高级工作站", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.pack(pady=(14, 2))
        self.subtitle_label = ctk.CTkLabel(
            self,
            text="心理咨询场景 · 实时生成 · 可视化播放",
            text_color="#8fa3c1",
            font=ctk.CTkFont(size=12),
        )
        self.subtitle_label.pack(pady=(0, 8))

        self.tabview = ctk.CTkTabview(self, width=860, height=700)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)

        self.tabview.add("🎙️ 语音合成")
        self.tabview.add("⚙️ 模型设置")

        self.setup_synthesis_tab()
        self.setup_settings_tab()
        self.bind("<Configure>", self.on_window_resize)

        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.pack(side="bottom", fill="x", padx=20, pady=8)
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="状态: 准备就绪", text_color="#8f96a3")
        self.status_label.pack(side="left")

        self.progress_info_frame = ctk.CTkFrame(self.status_frame, fg_color="#111827", corner_radius=10)
        self.progress_info_frame.pack(side="right", padx=(8, 0))

        self.progress_bar = ctk.CTkProgressBar(self.progress_info_frame, width=220, progress_color="#3b8ed0")
        self.progress_bar.pack(padx=10, pady=(8, 2))
        self.progress_bar.set(0)

        self.gen_time_label = ctk.CTkLabel(
            self.progress_info_frame,
            text="生成耗时: 0.0s",
            font=ctk.CTkFont(size=11),
            text_color="#c3c9d4",
        )
        self.gen_time_label.pack(padx=10, pady=(0, 8), anchor="e")

    def setup_synthesis_tab(self):
        tab = self.tabview.tab("🎙️ 语音合成")
        content = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=6, pady=6)
        
        self.viz_frame = ctk.CTkFrame(content, fg_color="#0d111c", height=150, corner_radius=14, border_width=1, border_color="#1f2937")
        self.viz_frame.pack(fill="x", padx=15, pady=10)
        self.viz_frame.pack_propagate(False)
        
        self.canvas = ctk.CTkCanvas(self.viz_frame, height=140, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, pady=5, padx=5)
        self.draw_static_viz()

        text_frame = ctk.CTkFrame(content)
        text_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(text_frame, text="📝 输入文本:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=5)
        
        self.textbox = ctk.CTkTextbox(text_frame, height=120, font=ctk.CTkFont(size=14))
        self.textbox.pack(fill="x", pady=5)
        self.textbox.insert("0.0", "在这里输入文字，点击生成后观察上方的可视化波形...")

        config_frame = ctk.CTkFrame(content, fg_color="transparent")
        config_frame.pack(fill="x", padx=15, pady=5)
        config_frame.grid_columnconfigure(0, weight=0)
        config_frame.grid_columnconfigure(1, weight=1)
        config_frame.grid_columnconfigure(2, weight=0)
        config_frame.grid_columnconfigure(3, weight=1)
        config_frame.grid_columnconfigure(4, weight=0)

        ctk.CTkLabel(config_frame, text="🎭 情感标签:", font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.emotions = QWEN_EMOTIONS
        self.emotion_dropdown = ctk.CTkComboBox(config_frame, values=self.emotions, width=200)
        self.emotion_dropdown.grid(row=0, column=1, padx=5, pady=8)
        self.emotion_dropdown.set(self.config.get("emotion", self.emotions[0]))

        ctk.CTkLabel(config_frame, text="🧩 人物人设:", font=ctk.CTkFont(size=12)).grid(row=0, column=2, padx=5, pady=8, sticky="w")
        self.personas = list(PERSONA_PRESETS.keys())
        self.persona_dropdown = ctk.CTkComboBox(config_frame, values=self.personas, width=150)
        self.persona_dropdown.grid(row=0, column=3, padx=5, pady=8)
        self.persona_dropdown.set(self.config.get("persona", self.personas[0]))

        ctk.CTkLabel(config_frame, text="🔥 情感强度:", font=ctk.CTkFont(size=12)).grid(row=2, column=2, padx=5, pady=8, sticky="w")
        self.emotion_intensity_slider = ctk.CTkSlider(config_frame, from_=0.6, to=1.4, number_of_steps=16, width=150)
        self.emotion_intensity_slider.grid(row=2, column=3, padx=5, pady=8)
        self.emotion_intensity_slider.set(self.config.get("emotion_intensity", 1.0))
        self.emotion_intensity_label = ctk.CTkLabel(config_frame, text=f"{self.emotion_intensity_slider.get():.2f}", font=ctk.CTkFont(size=11))
        self.emotion_intensity_label.grid(row=2, column=4, padx=2)
        self.emotion_intensity_slider.configure(command=self.on_emotion_intensity_change)

        ctk.CTkLabel(config_frame, text="🔊 音量:", font=ctk.CTkFont(size=12)).grid(row=1, column=2, padx=5, pady=8, sticky="w")
        self.volume_slider = ctk.CTkSlider(config_frame, from_=0, to=1, number_of_steps=20, width=150, command=self.on_volume_change)
        self.volume_slider.grid(row=1, column=3, padx=5, pady=8)
        self.volume_slider.set(self.config.get("volume", 0.8))
        
        self.volume_label = ctk.CTkLabel(config_frame, text=f"{int(self.volume_slider.get()*100)}%", font=ctk.CTkFont(size=11))
        self.volume_label.grid(row=1, column=4, padx=2)

        ctk.CTkLabel(config_frame, text="🎨 可视化:", font=ctk.CTkFont(size=12)).grid(row=2, column=0, padx=5, pady=8, sticky="w")
        self.viz_var = ctk.StringVar(value=self.config.get("viz_mode", "wave"))
        viz_seg = ctk.CTkSegmentedButton(config_frame, values=["wave", "bars", "circle"], variable=self.viz_var, command=self.change_viz_mode)
        viz_seg.grid(row=2, column=1, padx=5, pady=8, sticky="ew")

        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=10)

        self.action_button = ctk.CTkButton(
            button_frame,
            text="立即合成并播放",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=44,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            command=self.on_generate_click,
        )
        self.action_button.pack(side="left", expand=True, fill="x", padx=5)

        control_frame = ctk.CTkFrame(content, fg_color="transparent")
        control_frame.pack(fill="x", padx=15, pady=5)

        self.stop_button = ctk.CTkButton(control_frame, text="停止", width=110, height=35, 
                                          fg_color="#d32f2f", hover_color="#b71c1c", command=self.stop_playback)
        self.stop_button.pack(side="left", padx=5)

        self.pause_button = ctk.CTkButton(control_frame, text="暂停", width=110, height=35,
                                           command=self.toggle_pause)
        self.pause_button.pack(side="left", padx=5)

        self.replay_button = ctk.CTkButton(control_frame, text="重播", width=110, height=35,
                                            command=self.replay_audio)
        self.replay_button.pack(side="left", padx=5)

        self.save_button = ctk.CTkButton(control_frame, text="保存音频", width=110, height=35,
                                          fg_color="#388e3c", hover_color="#2e7d32", command=self.save_audio_file)
        self.save_button.pack(side="left", padx=5)

        self.history_frame = ctk.CTkFrame(content, corner_radius=10)
        self.history_frame.pack(fill="x", padx=15, pady=(8, 6))

        ctk.CTkLabel(self.history_frame, text="🕘 最近语音记录（最多10条）", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=(8, 4))

        history_action_frame = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        history_action_frame.pack(fill="x", padx=10, pady=(0, 10))
        history_action_frame.grid_columnconfigure(0, weight=1)
        history_action_frame.grid_columnconfigure(1, weight=0)
        history_action_frame.grid_columnconfigure(2, weight=0)
        history_action_frame.grid_columnconfigure(3, weight=0)
        history_action_frame.grid_columnconfigure(4, weight=0)

        self.history_dropdown = ctk.CTkComboBox(history_action_frame, values=["暂无历史记录"], width=560)
        self.history_dropdown.grid(row=0, column=0, columnspan=5, sticky="ew", padx=(2, 2), pady=(0, 8))
        self.history_dropdown.set("暂无历史记录")

        self.history_play_button = ctk.CTkButton(history_action_frame, text="播放记录", width=100, command=self.play_selected_history)
        self.history_play_button.grid(row=1, column=1, padx=4, sticky="e")

        self.history_load_text_button = ctk.CTkButton(history_action_frame, text="载入文本", width=100, command=self.load_selected_history_text)
        self.history_load_text_button.grid(row=1, column=2, padx=4)

        self.history_delete_button = ctk.CTkButton(history_action_frame, text="删除", width=80, fg_color="#6b7280", hover_color="#4b5563", command=self.delete_selected_history)
        self.history_delete_button.grid(row=1, column=3, padx=4)

        self.history_clear_button = ctk.CTkButton(history_action_frame, text="清空", width=80, fg_color="#7f1d1d", hover_color="#991b1b", command=self.clear_history)
        self.history_clear_button.grid(row=1, column=4, padx=(4, 2))

        self.refresh_history_ui()

    def start_generation_timer(self):
        self.stop_generation_timer(update_ui_only=True)
        self.is_generating = True
        self.gen_start_time = time.time()
        self.update_generation_timer()

    def update_generation_timer(self):
        if not self.is_generating:
            return

        elapsed = time.time() - self.gen_start_time if self.gen_start_time else 0.0
        self.gen_time_label.configure(text=f"生成耗时: {elapsed:.1f}s")
        # Simulated progress until file is returned; capped to avoid reaching 100% too early.
        simulated = min(0.92, 0.12 + elapsed / 20.0)
        self.progress_bar.set(max(self.progress_bar.get(), simulated))
        self.gen_timer_id = self.after(100, self.update_generation_timer)

    def stop_generation_timer(self, update_ui_only=False):
        if self.gen_timer_id:
            self.after_cancel(self.gen_timer_id)
            self.gen_timer_id = None

        elapsed = 0.0
        if self.gen_start_time:
            elapsed = max(0.0, time.time() - self.gen_start_time)

        self.is_generating = False
        self.gen_start_time = None

        if (not update_ui_only) and elapsed > 0:
            self.gen_time_label.configure(text=f"生成耗时: {elapsed:.1f}s")

        return elapsed

    def setup_settings_tab(self):
        tab = self.tabview.tab("⚙️ 模型设置")
        content = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=6, pady=6)
        
        ctk.CTkLabel(content, text="🔐 API 配置", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 10))
        
        self.url_entry = self.create_setting_item(content, "API URL:", self.config.get("api_url", "https://api.openai.com/v1/audio/speech"))
        self.key_entry = self.create_setting_item(content, "API Key:", self.config.get("api_key", "sk-..."), is_password=True)
        self.model_entry = self.create_setting_item(content, "默认模型:", self.config.get("model", "tts-1"))

        save_btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        save_btn_frame.pack(pady=20)
        
        ctk.CTkButton(save_btn_frame, text="💾 保存配置", width=150, command=self.save_config).pack(side="left", padx=10)
        ctk.CTkButton(save_btn_frame, text="🔄 重置默认", width=150, fg_color="gray", command=self.reset_config).pack(side="left", padx=10)

        ctk.CTkLabel(content, text="📋 使用说明", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))
        
        help_text = """1. 在「模型设置」中填写 API URL 与 API Key
2. 在「语音合成」标签页输入要转换的文本
3. 选择情感风格和语音角色
4. 点击「立即合成并播放」按钮
5. 使用控制按钮管理播放

    提示：
    - 若 API URL 为 /v1/tts，将自动使用本地 Qwen API 协议（x-api-key + WAV）
    - 本地 Qwen 模式默认使用内置适配器路径（可在配置文件中修改 adapter_path）
    - 情感与人设仅作为模型控制参数，不会被拼进正文，不会朗读“当前情感”字样
    - 其他 URL 默认按 OpenAI 兼容协议请求"""
        
        self.help_label = ctk.CTkLabel(content, text=help_text, justify="left", font=ctk.CTkFont(size=12), wraplength=780)
        self.help_label.pack(padx=20, pady=10, anchor="w")

    def create_setting_item(self, parent, label, default, is_password=False):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=40, pady=5)
        ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w")
        entry = ctk.CTkEntry(frame, width=500, show="●" if is_password else "")
        entry.pack(fill="x", pady=3)
        entry.insert(0, default)
        return entry

    def on_volume_change(self, value):
        self.volume = value
        self.volume_label.configure(text=f"{int(value*100)}%")
        pygame.mixer.music.set_volume(value)

    def on_emotion_intensity_change(self, value):
        self.emotion_intensity_label.configure(text=f"{float(value):.2f}")

    def draw_static_viz(self):
        self.canvas.delete("all")
        width = self.canvas.winfo_width() or 660
        height = 130
        
        self.canvas.create_line(0, height/2, width, height/2, fill="#333333", width=2)
        for i in range(0, width, 12):
            self.canvas.create_rectangle(i, height/2-2, i+6, height/2+2, fill="#333333", outline="")

    def update_viz_animation(self):
        if not self.is_playing:
            self.draw_static_viz()
            return

        self.canvas.delete("all")
        width = self.canvas.winfo_width() or 660
        height = 130
        t = time.time()
        
        if self.viz_mode == "wave":
            self.draw_wave_viz(width, height, t)
        elif self.viz_mode == "bars":
            self.draw_bars_viz(width, height, t)
        elif self.viz_mode == "circle":
            self.draw_circle_viz(width, height, t)

        self.animation_id = self.after(40, self.update_viz_animation)

    def draw_wave_viz(self, width, height, t):
        points = []
        for i in range(0, width, 3):
            y = height/2 + math.sin(i * 0.03 + t * 8) * 25 + random.randint(-10, 10)
            points.extend([i, y])
        
        if len(points) >= 4:
            self.canvas.create_line(points, fill="#3b8ed0", width=3, smooth=True)
        
        for i in range(0, width, 10):
            h = random.randint(10, 45) + abs(math.sin(i * 0.05 + t * 5)) * 20
            color = self.get_gradient_color(i, width)
            self.canvas.create_rectangle(i, height/2-h, i+6, height/2+h, fill=color, outline="")

    def draw_bars_viz(self, width, height, t):
        bar_width = 8
        gap = 4
        num_bars = int(width / (bar_width + gap))
        
        for i in range(num_bars):
            x = i * (bar_width + gap)
            h = random.randint(10, 50) + abs(math.sin(i * 0.3 + t * 6)) * 30
            color = self.get_gradient_color(i, num_bars)
            self.canvas.create_rectangle(x, height/2-h, x+bar_width, height/2+h, fill=color, outline="")

    def draw_circle_viz(self, width, height, t):
        cx, cy = width/2, height/2
        base_r = 40
        
        for i in range(36):
            angle = i * 10 * math.pi / 180
            r = base_r + random.randint(-15, 25) + math.sin(t * 5 + i * 0.5) * 15
            x1 = cx + r * math.cos(angle)
            y1 = cy + r * math.sin(angle)
            x2 = cx + (r + 8) * math.cos(angle)
            y2 = cy + (r + 8) * math.sin(angle)
            color = self.get_gradient_color(i, 36)
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=3)
        
        self.canvas.create_oval(cx-35, cy-35, cx+35, cy+35, outline="#3b8ed0", width=2)

    def get_gradient_color(self, index, total):
        ratio = index / total
        r = int(59 + ratio * (100 - 59))
        g = int(142 + ratio * (180 - 142))
        b = int(208 + ratio * (220 - 208))
        return f"#{r:02x}{g:02x}{b:02x}"

    def on_generate_click(self):
        text = self.textbox.get("0.0", "end").strip()
        if not text or text == "在这里输入文字，点击生成后观察上方的可视化波形...":
            messagebox.showwarning("提示", "请输入要合成的文本！")
            return
        
        api_url = self.url_entry.get().strip()
        api_key = self.key_entry.get().strip()
        normalized_url = self.normalize_api_url(api_url)
        is_local_qwen = normalized_url.rstrip("/").endswith("/v1/tts")
        
        if (not is_local_qwen) and (not api_key or api_key == "sk-..."):
            messagebox.showwarning("提示", "请在「模型设置」中配置有效的 API Key！")
            return

        if is_local_qwen and (not api_key or api_key == "sk-..."):
            # Local API only validates that x-api-key exists.
            api_key = "sk-test"
            self.key_entry.delete(0, "end")
            self.key_entry.insert(0, api_key)

        model = self.model_entry.get().strip() or self.config.get("model", "tts-1")
        persona = self.persona_dropdown.get()
        emotion_info = self.emotion_dropdown.get()
        self.action_button.configure(state="disabled", text="正在生成...")
        self.progress_bar.set(0.12)
        self.status_label.configure(text=f"状态: 正在合成语音（{emotion_info} / {persona}）...", text_color="orange")
        self.start_generation_timer()

        threading.Thread(
            target=self.run_tts,
            args=(text, persona, emotion_info, normalized_url, api_key, model),
            daemon=True,
        ).start()

    def run_tts(self, text, persona, emotion_info, url, key, model):
        try:
            url = self.normalize_api_url(url)
            profile = self.get_persona_profile(persona)
            emotion_key = self.map_emotion_for_qwen()
            controls = self.build_qwen_controls(profile=profile, emotion_key=emotion_key)
            read_timeout = self.estimate_read_timeout(text)

            # Auto-detect local Qwen API mode by endpoint path.
            if url.rstrip("/").endswith("/v1/tts"):
                filename = f"out_{int(time.time())}.wav"
                headers = {"x-api-key": key, "Content-Type": "application/json"}
                payload = {
                    "text": text,
                    "emotion": emotion_key,
                    "style": controls["style"],
                    "speed": controls["speed"],
                    "enhance_prosody": True,
                    "use_style_tags": True,
                    "x_vector_only_mode": True,
                    "do_sample": True,
                    "top_p": controls["top_p"],
                    "temperature": controls["temperature"],
                    "emotion_intensity": float(self.emotion_intensity_slider.get()),
                    "adapter_path": self.config.get("adapter_path", DEFAULT_LOCAL_ADAPTER),
                }
                ref_audio = self.resolve_ref_audio(persona)
                if ref_audio:
                    payload["ref_audio"] = ref_audio
            else:
                filename = f"out_{int(time.time())}.mp3"
                headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

                payload = {
                    "model": model,
                    "input": text,
                    "voice": profile["openai_voice"],
                    "response_format": "mp3"
                }

            try:
                resp = requests.post(url, json=payload, headers=headers, timeout=(10, read_timeout))
            except requests.exceptions.Timeout:
                # First call may include model warm-up; retry once with longer read timeout.
                resp = requests.post(url, json=payload, headers=headers, timeout=(10, read_timeout + 120))
            resp.raise_for_status()

            with open(filename, "wb") as f:
                f.write(resp.content)

            self.current_file = filename
            self.after(0, self.finish_generation_success, filename, text, persona, emotion_info)
        except requests.exceptions.Timeout:
            self.after(0, lambda: self.show_error("请求超时，请检查网络连接"))
        except requests.exceptions.ConnectionError:
            self.after(0, lambda: self.show_error("网络连接失败，请检查网络设置"))
        except requests.exceptions.HTTPError as e:
            self.after(0, lambda: self.show_error(f"API 错误: {e.response.status_code}"))
        except Exception as e:
            self.after(0, lambda: self.show_error(f"未知错误: {str(e)}"))

    def map_emotion_for_qwen(self):
        mapping = {
            "平静支持 (soothing)": "soothing",
            "温暖共情 (warm)": "warm",
            "冷静安抚 (calm)": "calm",
            "积极鼓励 (excited)": "excited",
            "庄重说明 (serious)": "serious",
            "探询引导 (inquisitive)": "inquisitive",
        }
        return mapping.get(self.emotion_dropdown.get(), "soothing")

    def get_persona_profile(self, persona_name):
        return PERSONA_PRESETS.get(persona_name, PERSONA_PRESETS["心理咨询师"])

    def build_qwen_controls(self, profile, emotion_key):
        emo = EMOTION_PROFILES.get(emotion_key, EMOTION_PROFILES["soothing"])
        intensity = float(self.emotion_intensity_slider.get())
        blend = max(0.2, min(0.85, 0.55 + (intensity - 1.0) * 0.5))

        top_p = profile["top_p"] * (1.0 - blend) + emo["top_p"] * blend
        temperature = profile["temperature"] * (1.0 - blend) + emo["temperature"] * blend
        speed = emo["speed"] if emotion_key in {"excited", "serious", "inquisitive"} else profile["speed"]

        return {
            "style": profile["style"],
            "speed": speed,
            "top_p": max(0.75, min(0.99, round(top_p, 3))),
            "temperature": max(0.55, min(1.05, round(temperature, 3))),
        }

    def resolve_ref_audio(self, persona_name):
        # Use persona-specific reference timbre if available.
        default_ref = "/root/autodl-tmp/dataset/Emotion Speech Dataset/0001/Neutral/0001_000001.wav"
        candidate = PERSONA_REF_AUDIO.get(persona_name, default_ref)
        if os.path.exists(candidate):
            return candidate
        return default_ref if os.path.exists(default_ref) else None

    def estimate_read_timeout(self, text):
        n = len(text.strip())
        # Longer text and cold model start require larger read timeout.
        return max(120, min(420, 60 + int(n * 1.8)))

    def normalize_api_url(self, url):
        raw = (url or "").strip()
        if not raw:
            return ""
        if raw.startswith("http://127.0.0.1:8000") or raw.startswith("http://localhost:8000"):
            if not raw.rstrip("/").endswith("/v1/tts"):
                return raw.rstrip("/") + "/v1/tts"
        return raw

    def show_error(self, message):
        self.stop_generation_timer()
        self.status_label.configure(text=f"错误: {message}", text_color="red")
        self.action_button.configure(state="normal", text="立即合成并播放")
        self.progress_bar.set(0)
        messagebox.showerror("错误", message)

    def finish_generation_success(self, filename, source_text, persona, emotion_info):
        elapsed = self.stop_generation_timer()
        self.add_to_history(filename, source_text, persona, emotion_info, elapsed)
        self.progress_bar.set(1.0)
        self.status_label.configure(text=f"状态: 合成完成，用时 {elapsed:.1f}s，开始播放", text_color="#3b8ed0")
        self.start_playback(filename)

    def add_to_history(self, filepath, text, persona, emotion_info, elapsed):
        abs_path = os.path.abspath(filepath)
        record = {
            "file": abs_path,
            "text": str(text or "").strip(),
            "persona": persona,
            "emotion": emotion_info,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "elapsed": round(float(elapsed or 0.0), 2),
        }

        # De-duplicate by file path then insert newest at top.
        self.audio_history = [r for r in self.audio_history if r.get("file") != abs_path]
        self.audio_history.insert(0, record)
        self.audio_history = self.audio_history[:10]
        self.config["audio_history"] = self.audio_history
        self.write_config_file(silent=True)
        self.refresh_history_ui()

    def history_item_label(self, record):
        ts = record.get("created_at", "")
        persona = record.get("persona", "未知人设")
        emo = record.get("emotion", "")
        txt = record.get("text", "")
        preview = txt[:16] + "..." if len(txt) > 16 else txt
        return f"{ts} | {persona} | {emo} | {preview}"

    def refresh_history_ui(self):
        valid = []
        for r in self.audio_history:
            f = r.get("file", "")
            if f and os.path.exists(f):
                valid.append(r)
        self.audio_history = valid[:10]
        self.config["audio_history"] = self.audio_history

        if not hasattr(self, "history_dropdown"):
            return

        if not self.audio_history:
            self.history_display_values = ["暂无历史记录"]
            self.history_dropdown.configure(values=self.history_display_values)
            self.history_dropdown.set("暂无历史记录")
            return

        self.history_display_values = [self.history_item_label(r) for r in self.audio_history]
        self.history_dropdown.configure(values=self.history_display_values)
        self.history_dropdown.set(self.history_display_values[0])

    def get_selected_history_index(self):
        if not self.audio_history:
            return None
        current = self.history_dropdown.get().strip()
        try:
            return self.history_display_values.index(current)
        except ValueError:
            return 0

    def play_selected_history(self):
        idx = self.get_selected_history_index()
        if idx is None:
            messagebox.showinfo("提示", "暂无可播放的历史记录")
            return
        rec = self.audio_history[idx]
        path = rec.get("file", "")
        if not path or (not os.path.exists(path)):
            messagebox.showwarning("提示", "该历史音频文件不存在，已自动清理。")
            self.refresh_history_ui()
            return
        self.current_file = path
        self.stop_playback()
        self.after(100, lambda: self.start_playback(path))

    def load_selected_history_text(self):
        idx = self.get_selected_history_index()
        if idx is None:
            messagebox.showinfo("提示", "暂无可加载文本的历史记录")
            return
        txt = self.audio_history[idx].get("text", "").strip()
        if not txt:
            messagebox.showinfo("提示", "该记录没有可用文本")
            return
        self.textbox.delete("0.0", "end")
        self.textbox.insert("0.0", txt)
        self.status_label.configure(text="状态: 已载入历史文本", text_color="#8f96a3")

    def delete_selected_history(self):
        idx = self.get_selected_history_index()
        if idx is None:
            messagebox.showinfo("提示", "暂无可删除的历史记录")
            return
        self.audio_history.pop(idx)
        self.config["audio_history"] = self.audio_history
        self.write_config_file(silent=True)
        self.refresh_history_ui()

    def clear_history(self):
        if not self.audio_history:
            messagebox.showinfo("提示", "历史记录已经为空")
            return
        if not messagebox.askyesno("确认", "确定清空最近语音历史吗？"):
            return
        self.audio_history = []
        self.config["audio_history"] = []
        self.write_config_file(silent=True)
        self.refresh_history_ui()

    def start_playback(self, filename):
        try:
            pygame.mixer.music.load(filename)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()
            
            self.is_playing = True
            self.is_paused = False
            self.pause_button.configure(text="暂停")
            self.update_viz_animation()
            
            self.progress_bar.set(1.0)
            self.status_label.configure(text="状态: 正在播放...", text_color="#3b8ed0")
            self.check_music_end()
        except Exception as e:
            self.show_error(f"播放失败: {str(e)}")

    def check_music_end(self):
        if pygame.mixer.music.get_busy():
            self.after(100, self.check_music_end)
        else:
            self.is_playing = False
            self.status_label.configure(text="状态: 播放完毕", text_color="gray")
            self.action_button.configure(state="normal", text="立即合成并播放")
            self.progress_bar.set(0)
            self.draw_static_viz()

    def stop_playback(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.pause_button.configure(text="暂停")
        self.status_label.configure(text="状态: 已停止", text_color="gray")
        self.action_button.configure(state="normal", text="立即合成并播放")
        self.progress_bar.set(0)
        self.draw_static_viz()

    def toggle_pause(self):
        if not self.is_playing:
            return
        
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.pause_button.configure(text="暂停")
            self.status_label.configure(text="状态: 正在播放...", text_color="#3b8ed0")
            self.update_viz_animation()
        else:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.pause_button.configure(text="继续")
            self.status_label.configure(text="状态: 已暂停", text_color="orange")

    def replay_audio(self):
        if self.current_file and os.path.exists(self.current_file):
            self.stop_playback()
            self.after(100, lambda: self.start_playback(self.current_file))
        else:
            messagebox.showinfo("提示", "没有可重播的音频，请先生成！")

    def save_audio_file(self):
        if not self.current_file or not os.path.exists(self.current_file):
            messagebox.showinfo("提示", "没有可保存的音频，请先生成！")
            return

        ext = os.path.splitext(self.current_file)[1].lower()
        if ext not in [".mp3", ".wav"]:
            ext = ".mp3"
        filetypes = [("音频文件", "*.mp3 *.wav"), ("MP3 文件", "*.mp3"), ("WAV 文件", "*.wav"), ("所有文件", "*.*")]
        
        save_path = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=filetypes,
            title="保存音频文件"
        )
        
        if save_path:
            try:
                import shutil
                shutil.copy(self.current_file, save_path)
                messagebox.showinfo("成功", f"音频已保存到:\n{save_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")

    def load_config(self):
        default_config = {
            "api_url": "http://127.0.0.1:8000/v1/tts",
            "api_key": "sk-...",
            "model": "tts-1",
            "adapter_path": DEFAULT_LOCAL_ADAPTER,
            "emotion_intensity": 1.0,
            "persona": "心理咨询师",
            "emotion": "平静支持 (soothing)",
            "volume": 0.8,
            "viz_mode": "wave",
            "audio_history": [],
        }
        
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self.config = {**default_config, **json.load(f)}
            else:
                self.config = default_config

            # Backward-compatible migration for older config keys/values.
            if not self.config.get("persona"):
                old_voice = self.config.get("voice", "nova")
                voice_to_persona = {
                    "alloy": "理性分析师",
                    "echo": "成长教练",
                    "fable": "温柔倾听者",
                    "onyx": "理性分析师",
                    "nova": "心理咨询师",
                    "shimmer": "温柔倾听者",
                }
                self.config["persona"] = voice_to_persona.get(old_voice, "心理咨询师")

            old_emotion_map = {
                "😊 平静 (Neutral)": "平静支持 (soothing)",
                "🌟 兴奋 (Excited)": "积极鼓励 (excited)",
                "🤝 亲切 (Friendly)": "温暖共情 (warm)",
                "😔 悲伤 (Sad)": "冷静安抚 (calm)",
                "🔥 愤怒 (Angry)": "庄重说明 (serious)",
                "🌬️ 轻柔 (Whispering)": "冷静安抚 (calm)",
                "📢 庄重 (Serious)": "庄重说明 (serious)",
                "🤔 疑惑 (Inquisitive)": "探询引导 (inquisitive)",
            }
            self.config["emotion"] = old_emotion_map.get(self.config.get("emotion"), self.config.get("emotion"))

            if self.config.get("persona") not in PERSONA_PRESETS:
                self.config["persona"] = "心理咨询师"
            if self.config.get("emotion") not in QWEN_EMOTIONS:
                self.config["emotion"] = "平静支持 (soothing)"
            if not self.config.get("adapter_path"):
                self.config["adapter_path"] = DEFAULT_LOCAL_ADAPTER
            self.config["emotion_intensity"] = float(self.config.get("emotion_intensity", 1.0))
            self.config["emotion_intensity"] = max(0.6, min(1.4, self.config["emotion_intensity"]))
            self.audio_history = list(self.config.get("audio_history", []))[:10]
        except:
            self.config = default_config
            self.audio_history = []

    def write_config_file(self, silent=False):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            if not silent:
                messagebox.showinfo("成功", "配置已保存！")
            return True
        except Exception as e:
            if not silent:
                messagebox.showerror("错误", f"保存配置失败: {str(e)}")
            return False

    def save_config(self):
        self.config["api_url"] = self.url_entry.get().strip()
        self.config["api_key"] = self.key_entry.get().strip()
        self.config["model"] = self.model_entry.get().strip()
        self.config["emotion_intensity"] = float(self.emotion_intensity_slider.get())
        self.config["persona"] = self.persona_dropdown.get()
        self.config["emotion"] = self.emotion_dropdown.get()
        self.config["volume"] = self.volume_slider.get()
        self.config["viz_mode"] = self.viz_var.get()
        self.config["audio_history"] = self.audio_history[:10]
        self.write_config_file(silent=False)

    def reset_config(self):
        if messagebox.askyesno("确认", "确定要重置所有配置吗？"):
            self.config = {
                "api_url": "http://127.0.0.1:8000/v1/tts",
                "api_key": "sk-...",
                "model": "tts-1",
                "adapter_path": DEFAULT_LOCAL_ADAPTER,
                "emotion_intensity": 1.0,
                "persona": "心理咨询师",
                "emotion": "平静支持 (soothing)",
                "volume": 0.8,
                "viz_mode": "wave",
                "audio_history": [],
            }
            self.audio_history = []
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, self.config["api_url"])
            self.key_entry.delete(0, "end")
            self.key_entry.insert(0, self.config["api_key"])
            self.model_entry.delete(0, "end")
            self.model_entry.insert(0, self.config["model"])
            self.emotion_intensity_slider.set(self.config["emotion_intensity"])
            self.on_emotion_intensity_change(self.config["emotion_intensity"])
            self.persona_dropdown.set(self.config["persona"])
            self.emotion_dropdown.set(self.config["emotion"])
            self.volume_slider.set(self.config["volume"])
            self.refresh_history_ui()
            messagebox.showinfo("成功", "配置已重置！")

    def on_window_resize(self, event):
        if event.widget != self:
            return
        if self.resize_job:
            self.after_cancel(self.resize_job)
        self.resize_job = self.after(120, self.apply_responsive_layout)

    def apply_responsive_layout(self):
        self.resize_job = None
        w = self.winfo_width()

        if hasattr(self, "help_label"):
            self.help_label.configure(wraplength=max(520, w - 180))

        if hasattr(self, "history_dropdown"):
            self.history_dropdown.configure(width=max(420, w - 320))

        if hasattr(self, "textbox"):
            self.textbox.configure(height=100 if w < 980 else 120)

        if not self.is_playing and hasattr(self, "canvas"):
            self.draw_static_viz()

    def change_viz_mode(self, mode):
        self.viz_mode = mode
        if not self.is_playing:
            self.draw_static_viz()

    def on_closing(self):
        if self.animation_id:
            self.after_cancel(self.animation_id)
        if self.gen_timer_id:
            self.after_cancel(self.gen_timer_id)
        pygame.mixer.quit()
        self.destroy()

if __name__ == "__main__":
    app = AdvancedTTSApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
