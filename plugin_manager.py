"""
插件管理器 - 支持动态加载和管理插件
"""
import importlib
import os
from typing import Dict, List, Any
from abc import ABC, abstractmethod


class PluginBase(ABC):
    """插件基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """插件版本"""
        pass
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行插件逻辑"""
        pass
    
    def on_load(self):
        """插件加载时的初始化"""
        pass
    
    def on_unload(self):
        """插件卸载时的清理"""
        pass


class PluginManager:
    """插件管理器"""
    
    def __init__(self, plugin_dir: str = "./plugins"):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, PluginBase] = {}
        os.makedirs(plugin_dir, exist_ok=True)
    
    def load_plugin(self, plugin_name: str) -> bool:
        """加载单个插件"""
        try:
            # 动态导入插件模块
            import importlib.util
            import sys
            
            plugin_path = os.path.join(self.plugin_dir, f"{plugin_name}.py")
            
            if not os.path.exists(plugin_path):
                print(f"错误: 插件文件不存在 {plugin_path}")
                return False
            
            # 确保当前目录在 sys.path 中
            if os.getcwd() not in sys.path:
                sys.path.insert(0, os.getcwd())
            
            spec = importlib.util.spec_from_file_location(f"plugins.{plugin_name}", plugin_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            
            plugin_class = getattr(module, "Plugin", None)
            if plugin_class is None:
                print(f"错误: {plugin_name} 中找不到 Plugin 类")
                return False
            
            plugin = plugin_class()
            
            # 检查是否有必要的属性和方法
            required_attrs = ['name', 'version', 'execute']
            for attr in required_attrs:
                if not hasattr(plugin, attr):
                    print(f"错误: {plugin_name} 缺少必要属性/方法: {attr}")
                    return False
            
            plugin.on_load()
            self.plugins[plugin.name] = plugin
            print(f"✓ 插件已加载: {plugin.name} v{plugin.version}")
            return True
        except Exception as e:
            print(f"✗ 加载插件失败 {plugin_name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_all_plugins(self):
        """加载所有插件"""
        if not os.path.exists(self.plugin_dir):
            return
        
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                plugin_name = filename[:-3]
                self.load_plugin(plugin_name)
    
    def unload_plugin(self, plugin_name: str):
        """卸载插件"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].on_unload()
            del self.plugins[plugin_name]
            print(f"✓ 插件已卸载: {plugin_name}")
    
    def execute_plugin(self, plugin_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行指定插件"""
        if plugin_name not in self.plugins:
            raise ValueError(f"插件不存在: {plugin_name}")
        
        return self.plugins[plugin_name].execute(context)
    
    def get_available_plugins(self) -> List[str]:
        """获取已加载的插件列表"""
        return list(self.plugins.keys())
    
    def get_plugin_info(self, plugin_name: str) -> Dict[str, str]:
        """获取插件信息"""
        if plugin_name not in self.plugins:
            return {}
        
        plugin = self.plugins[plugin_name]
        return {
            "name": plugin.name,
            "version": plugin.version,
            "description": getattr(plugin, "description", "无描述")
        }


if __name__ == "__main__":
    # 测试插件管理器
    manager = PluginManager()
    manager.load_all_plugins()
    print(f"\n已加载插件: {manager.get_available_plugins()}")
