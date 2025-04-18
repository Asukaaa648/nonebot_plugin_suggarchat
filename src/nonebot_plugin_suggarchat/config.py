import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import nonebot_plugin_localstore as store
import tomli
import tomli_w
from pydantic import BaseModel

__KERNEL_VERSION__ = "unknow"

# 保留为其他插件提供的引用

# 配置目录
CONFIG_DIR: Path = store.get_plugin_config_dir()
DATA_DIR: Path = store.get_plugin_data_dir()


class ModelPreset(BaseModel, extra="allow"):
    model: str = "__main__"
    name: str = ""
    base_url: str = ""
    api_key: str = ""
    protocol: str = "__main__"

    @classmethod
    def load(cls, path: Path):
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return cls(**data)
        return cls()  # 返回默认值

    def save(self, path: Path):
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, indent=4, ensure_ascii=False)

    def __getattr__(self, item) -> str:
        if item in self.__dict__:
            return self.__dict__[item]
        if self.__pydantic_extra__ and item in self.__pydantic_extra__:
            return self.__pydantic_extra__[item]
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{item}'"
        )


class Config(BaseModel, extra="allow"):
    preset: str = ModelPreset().model
    memory_lenth_limit: int = 50
    enable: bool = False
    fake_people: bool = False
    probability: float = 1e-2
    keyword: str = "at"
    nature_chat_style: bool = True
    poke_reply: bool = True
    enable_group_chat: bool = True
    enable_private_chat: bool = True
    allow_custom_prompt: bool = True
    allow_send_to_admin: bool = False
    use_base_prompt: bool = True
    admin_group: int = 0
    admins: list[int] = []
    open_ai_base_url: str = ModelPreset().base_url
    open_ai_api_key: str = ModelPreset().api_key
    stream: bool = False
    max_tokens: int = 100
    tokens_count_mode: str = "bpe"
    session_max_tokens: int = 5000
    enable_tokens_limit: bool = True
    model: str = "auto"
    llm_timeout: int = 60
    say_after_self_msg_be_deleted: bool = False
    group_added_msg: str = "你好，我是Suggar，欢迎使用Suggar的AI聊天机器人..."
    send_msg_after_be_invited: bool = False
    after_deleted_say_what: list[str] = [
        "Suggar说错什么话了吗～下次我会注意的呢～",
        "抱歉啦，不小心说错啦～",
        "嘿，发生什么事啦？我",
        "唔，我是不是说错了什么？",
        "纠错时间到，如果我说错了请告诉我！",
        "发生了什么？我刚刚没听清楚呢~",
        "我能帮你做点什么吗？不小心说错话了让我变得不那么尴尬~",
        "我会记住的，绝对不再说错话啦~",
        "哦，看来我又犯错了，真是不好意思！",
        "哈哈，看来我得多读书了~",
        "哎呀，真是个小口误，别在意哦~",
        "Suggar苯苯的，偶尔说错话很正常嘛！",
        "哎呀，我也有尴尬的时候呢~",
        "希望我能继续为你提供帮助，不要太在意我的小错误哦！",
    ]
    parse_segments: bool = True
    protocol: str = "__main__"
    matcher_function: bool = True
    session_control: bool = False
    session_control_time: int = 60
    session_control_history: int = 10
    group_prompt_character: str = "default"
    private_prompt_character: str = "default"

    # Toml配置文件路径
    @classmethod
    def load_from_toml(cls, path: Path) -> "Config":
        """从 TOML 文件加载配置"""
        if path.exists():
            with path.open("rb") as f:
                data: dict[str, Any] = tomli.load(f)
            # 自动更新配置文件
            current_config = cls().model_dump()
            updated_config = {**current_config, **data}
            config_instance = cls(**updated_config)
            if current_config != updated_config:
                config_instance.save_to_toml(path)
            return config_instance
        return cls()

    @classmethod
    def load_from_json(cls, path: Path) -> "Config":
        """从 JSON 文件加载配置"""
        with path.open("r", encoding="utf-8") as f:
            data: dict = json.load(f)
        return cls(**data)

    def save_to_toml(self, path: Path):
        """保存配置到 TOML 文件"""
        with path.open("wb") as f:
            tomli_w.dump(self.model_dump(), f)

    def __getattr__(self, item) -> str:
        if item in self.__dict__:
            return self.__dict__[item]
        if self.__pydantic_extra__ and item in self.__pydantic_extra__:
            return self.__pydantic_extra__[item]
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{item}'"
        )


@dataclass
class Prompt:
    text: str = ""
    name: str = "default"


@dataclass
class Prompts:
    group: list[Prompt] = field(default_factory=list)
    private: list[Prompt] = field(default_factory=list)
    def save_group(self, path: Path):
        """保存群组提示词"""
        for prompt in self.group:
            with (path / f"{prompt.name}.txt").open("w", encoding="utf-8") as f:
                f.write(prompt.text)

    def save_private(self, path: Path):
        """保存私聊提示词"""
        for prompt in self.private:
            with (path / f"{prompt.name}.txt").open("w", encoding="utf-8") as f:
                f.write(prompt.text)


@dataclass
class ConfigManager:
    config_dir: Path = CONFIG_DIR
    data_dir: Path = DATA_DIR
    group_memory: Path = data_dir / "group"
    private_memory: Path = data_dir / "private"
    json_config: Path = config_dir / "config.json"  # 兼容旧版本
    toml_config: Path = config_dir / "config.toml"
    group_prompt: Path = config_dir / "prompt_group.txt"  # 兼容旧版本
    private_prompt: Path = config_dir / "prompt_private.txt"  # 兼容旧版本
    private_prompts: Path = config_dir / "private_prompts"
    group_prompts: Path = config_dir / "group_prompts"
    custom_models_dir: Path = config_dir / "models"
    private_train: dict = field(default_factory=dict)
    group_train: dict = field(default_factory=dict)
    config: Config = field(default_factory=Config)
    models: list[tuple[ModelPreset, str]] = field(default_factory=list)

    prompts: Prompts = field(default_factory=Prompts)

    def load(self, bot_id: str):
        """初始化配置目录"""
        self.config_dir = self.config_dir / bot_id
        self.data_dir = self.data_dir / bot_id
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)

        self.group_memory = self.data_dir / "group"
        self.private_memory = self.data_dir / "private"
        os.makedirs(self.group_memory, exist_ok=True)
        os.makedirs(self.private_memory, exist_ok=True)

        self.json_config = self.config_dir / "config.json"
        self.toml_config = self.config_dir / "config.toml"
        self.group_prompt = self.config_dir / "prompt_group.txt"
        self.private_prompt = self.config_dir / "prompt_private.txt"
        self.private_prompts = self.config_dir / "private_prompts"
        self.group_prompts = self.config_dir / "group_prompts"
        os.makedirs(self.private_prompts, exist_ok=True)
        os.makedirs(self.group_prompts, exist_ok=True)
        self.custom_models_dir = self.config_dir / "models"
        os.makedirs(self.custom_models_dir, exist_ok=True)

        # 处理配置文件转换
        if self.json_config.exists():
            with self.json_config.open("r", encoding="utf-8") as f:
                data: dict = json.load(f)

            # 判断是否有抛弃的字段需要转移
            if "private_train" in data:
                prompt_old = data["private_train"]["content"]
                if not (self.private_prompts / "default.txt").is_file():
                    with (self.private_prompts / "default.txt").open(
                        "w", encoding="utf-8"
                    ) as f:
                        f.write(prompt_old)
                del data["private_train"]

            if "group_train" in data:
                prompt_old = data["group_train"]["content"]
                if not (self.group_prompts / "default.txt").is_file():
                    with (self.group_prompts / "default.txt").open(
                        "w", encoding="utf-8"
                    ) as f:
                        f.write(prompt_old)
                del data["group_train"]

            Config(**data).save_to_toml(self.toml_config)
            os.rename(self.json_config, self.json_config.with_suffix(".old"))
            self.config = Config.load_from_toml(self.toml_config)

        elif self.toml_config.exists():
            self.config = Config.load_from_toml(self.toml_config)
        else:
            self.config = Config()
            self.config.save_to_toml(self.toml_config)

        # private_train
        prompt = ""
        if self.private_prompt.is_file():
            with self.private_prompt.open("r", encoding="utf-8") as f:
                prompt = f.read()
            os.rename(self.private_prompt, self.private_prompt.with_suffix(".old"))
        if not (self.private_prompts / "default.txt").is_file():
            with (self.private_prompts / "default.txt").open(
                "w", encoding="utf-8"
            ) as f:
                f.write(prompt)

        # group_train
        prompt = ""
        if self.group_prompt.is_file():
            with self.group_prompt.open("r", encoding="utf-8") as f:
                prompt = f.read()
            os.rename(self.group_prompt, self.group_prompt.with_suffix(".old"))
        if not (self.group_prompts / "default.txt").is_file():
            with (self.group_prompts / "default.txt").open("w", encoding="utf-8") as f:
                f.write(prompt)

        self.get_models(cache=False)
        self.get_prompts(cache=False)
        self.load_prompt()

    def get_models(self, cache: bool = False) -> list[ModelPreset]:
        """获取模型列表"""
        if cache and self.models:
            return [model[0] for model in self.models]
        self.models.clear()
        for file in self.custom_models_dir.glob("*.json"):
            self.models.append((ModelPreset.load(file), file.stem))
        return [model[0] for model in self.models]

    def get_prompts(self, cache: bool = False) -> Prompts:
        """获取提示词"""
        if cache and self.prompts:
            return self.prompts
        self.prompts = Prompts()
        for file in self.private_prompts.glob("*.txt"):
            with file.open("r", encoding="utf-8") as f:
                prompt = f.read()
            self.prompts.private.append(Prompt(prompt, file.stem))
        for file in self.group_prompts.glob("*.txt"):
            with file.open("r", encoding="utf-8") as f:
                prompt = f.read()
            self.prompts.group.append(Prompt(prompt, file.stem))
        if not self.prompts.private:
            self.prompts.private.append(Prompt("", "default"))
        if not self.prompts.group:
            self.prompts.group.append(Prompt("", "default"))

        self.prompts.save_private(self.private_prompts)
        self.prompts.save_group(self.group_prompts)

        return self.prompts

    def load_prompt(self):
        """加载提示词，匹配预设"""
        for prompt in self.prompts.group:
            if prompt.name == self.config.group_prompt_character:
                self.group_train = {"role": "system", "content": prompt.text}
                break
        else:
            raise ValueError(
                f"没有找到名称为 {self.config.group_prompt_character} 的群组提示词"
            )
        for prompt in self.prompts.private:
            if prompt.name == self.config.private_prompt_character:
                self.private_train = {"role": "system", "content": prompt.text}
                break
        else:
            raise ValueError(
                f"没有找到名称为 {self.config.private_prompt_character} 的私聊提示词"
            )

    def reload_config(self):
        """重加载配置"""
        self.load(self.config_dir.name)

    def save_config(self):
        """保存配置"""
        if self.config:
            self.config.save_to_toml(self.toml_config)

    def set_config(self, key: str, value: str):
        """
        设置配置

        :param key: 配置项的名称
        :param value: 配置项的值

        :raises KeyError: 如果配置项不存在，则抛出异常
        """
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            self.save_config()
        else:
            raise KeyError(f"配置项 {key} 不存在")
    def register_config(self, key: str, default_value=None):
        """
        注册配置项

        :param key: 配置项的名称

        """
        if default_value is None:
            default_value = "null"
        if not hasattr(self.config, key):
            setattr(self.config, key, default_value)
        self.save_config()

    def reg_config(self, key: str, default_value=None):
        """
        注册配置项

        :param key: 配置项的名称

        """
        return self.register_config(key, default_value)

    def reg_model_config(self, key: str, default_value=None):
        """
        注册模型配置项

        :param key: 配置项的名称

        """
        if default_value is None:
            default_value = "null"
        for model in self.models:
            if not hasattr(model[0], key):
                setattr(model[0], key, default_value)
            model[0].save(self.custom_models_dir / f"{model[1]}.json")


config_manager = ConfigManager()
