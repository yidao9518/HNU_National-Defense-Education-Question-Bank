from webdriver_manager.microsoft import EdgeChromiumDriverManager
import ssl

# 禁用SSL验证
# ssl._create_default_https_context = ssl._create_unverified_context

def save_driver_path():
    """获取并保存路径"""
    # 获取驱动路径（会自动下载或使用缓存的）
    driver_path = EdgeChromiumDriverManager().install()

    # 保存到文件
    with open('driver_path.txt', 'w', encoding = 'utf-8') as f:
        f.write(driver_path)

    print(f"驱动路径已保存: {driver_path}")
    return driver_path


def load_driver_path():
    """从文件加载路径"""
    try:
        with open('driver_path.txt', 'r', encoding = 'utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        print("驱动路径文件不存在，将重新获取")
        return save_driver_path()

if __name__ == "__main__":
    # 保存驱动路径
    save_driver_path()

    # 加载驱动路径
    driver_path = load_driver_path()
    print(f"加载的驱动路径: {driver_path}")
