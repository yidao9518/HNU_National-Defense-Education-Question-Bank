# 湖南大学国防教育问卷自动填写程序

本项目用于自动填写湖南大学国防教育问卷星问卷，适合批量自动化填写。程序基于 Python 和 Selenium，默认支持 Edge 浏览器。

## 使用方法

1. **运行方式**  
   直接执行 `auto_ans_new.py` 文件即可自动填写问卷。可以在AutoFiller.wait()中修改题目等待时间 

2. **浏览器支持**  
   默认支持 Edge 浏览器。如果需使用其他浏览器，请修改 `get_driver_path.py` 文件，并下载对应浏览器驱动。

3. **浏览器驱动下载**  
   - Edge 驱动：[Microsoft Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)
   - Chrome 驱动：[ChromeDriver](https://chromedriver.chromium.org/downloads)
   - Firefox 驱动：[GeckoDriver](https://github.com/mozilla/geckodriver/releases)

4. **依赖软件包**

   - `selenium`
   - `logging`
   - `re`
   - `time`
   - `random`

   安装依赖：

   ```bash
   pip install selenium