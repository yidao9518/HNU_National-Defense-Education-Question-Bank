from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import logging
import time

import get_driver_path

# 设置日志
logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AutoFiller:
    """自动填写问卷"""

    def __init__(self, headless = False):
        """ :param headless: 是否无头模式（默认False，即显示浏览器界面）"""
        logger.info("初始化自动填写问卷工具")
        self.driver = None
        self.headless = headless
        self.setup_driver()

    def setup_driver(self):
        """设置浏览器驱动"""
        options = Options()

        # 反检测
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # 其他配置
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')

        if self.headless:
            options.add_argument('--headless')

        # 配置驱动服务
        service = Service(executable_path = get_driver_path.load_driver_path())

        try:
            self.driver = webdriver.Edge(service = service, options = options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument',
                                        {
                                            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'})
            logger.info("浏览器驱动初始化成功")
        except Exception as e:
            logger.error(f"浏览器驱动初始化失败: {e}")
            raise

    def click(self, element):
        logger.debug(f"尝试JavaScript点击: ")
        try:
            self.driver.execute_script("""
                        var element = arguments[0];
                        // 触发点击事件
                        var clickEvent = new MouseEvent('click', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        element.dispatchEvent(clickEvent);

                        // 触发input事件
                        var inputEvent = new Event('input', {
                            bubbles: true
                        });
                        element.dispatchEvent(inputEvent);

                        // 设置checked属性
                        element.checked = true;
                    """, element)
            logger.debug("JavaScript点击成功")
            return True
        except Exception as js_error:
            logger.error(f"JavaScript点击失败: {js_error}")
            return False

    @staticmethod
    def type(element, text):
        """输入文本"""
        try:
            element.clear()
            for char in text: element.send_keys(char)
            return True
        except Exception as e:
            logger.error(f"输入文本失败: {e}")
            return False

    @staticmethod
    def wait():
        time.sleep(5)
        # pass

    def find_question_elements(self):
        """查找题目元素"""

        textarea_elements = []
        radio_4_topics = []
        radio_4_input_elements = []
        checkbox_4_topics = []
        checkbox_4_input_elements = []
        radio_2_topics = []
        radio_2_input_elements = []

        try:
            container = self.driver.find_element(By.XPATH, "//*[@id='divQuestion']")

            textarea_elements += [
                container.find_element(By.XPATH, f"./fieldset[1]/div[1]/table/tbody/tr[{i}]/td[2]/div/textarea")
                for i in (2, 4)
            ]

            for pg in range(1, 26):
                div = container.find_element(By.XPATH,
                                             f"./fieldset[@pg='{pg}']/div[@class='field ui-field-contain lxhide']")
                radio_4_topics.append(div.get_attribute("topic"))
                radio_4_input_elements_temp = []
                for value in range(1, 5):
                    try:
                        element = div.find_element(By.XPATH, f".//input[@type='radio' and @value='{value}']")
                        radio_4_input_elements_temp.append(element)
                    except Exception as e:
                        logger.warning(f"未找到单选按钮 pg={pg}, value={value}: {e}")
                radio_4_input_elements.append(radio_4_input_elements_temp)

            for pg in range(59, 64):
                div = container.find_element(By.XPATH,
                                             f"./fieldset[@pg='{pg}']/div[@class='field ui-field-contain lxhide']")
                checkbox_4_topics.append(div.get_attribute("topic"))
                checkbox_4_input_elements_temp = []
                for value in range(1, 5):
                    try:
                        element = div.find_element(By.XPATH, f".//input[@type='checkbox' and @value='{value}']")
                        checkbox_4_input_elements_temp.append(element)
                    except Exception as e:
                        logger.warning(f"未找到多选按钮 pg={pg}, value={value}: {e}")
                checkbox_4_input_elements.append(checkbox_4_input_elements_temp)

            for pg in range(68, 78):
                div = container.find_element(By.XPATH,
                                             f"./fieldset[@pg='{pg}']/div[@class='field ui-field-contain lxhide']")
                radio_2_topics.append(div.get_attribute("topic"))
                radio_2_input_elements_temp = []
                for value in range(1, 3):
                    try:
                        element = div.find_element(By.XPATH, f".//input[@type='radio' and @value='{value}']")
                        radio_2_input_elements_temp.append(element)
                    except Exception as e:
                        logger.warning(f"未找到单选按钮 pg={pg}, value={value}: {e}")
                radio_2_input_elements.append(radio_2_input_elements_temp)

            logger.info("题目元素查找成功")
            return textarea_elements, (radio_4_topics, radio_4_input_elements), (
                checkbox_4_topics, checkbox_4_input_elements), (radio_2_topics, radio_2_input_elements)

        except Exception as e:
            logger.error(f"查找题目元素失败: {e}")
            return [], None, None, None

    def start_questionnaire(self):
        """点击开始问卷按钮"""
        try:
            start_button = self.driver.find_element(By.CSS_SELECTOR, ".lxstartBtn.mainBgColor")
            self.click(start_button)
            logger.info("开始答题")
            return True

        except Exception as e:
            logger.warning(f"未找到开始按钮或无法点击:{e}")
            return False

    def go_to_next_page(self):
        """点击下一页按钮"""
        try:
            next_button = WebDriverWait(self.driver, 1).until(
                expected_conditions.element_to_be_clickable((By.ID, "lxNextBtn"))
            )
            logger.info("找到下一页按钮")
            next_button.click()
            return True

        except Exception as e:
            logger.warning(f"未找到下一页按钮或无法点击:{e}")
            return False

    def get_ans(self):
        """获取答案"""
        ans_radio_4 = {}
        ans_checkbox_4 = {}
        ans_radio_2 = {}

        # 等待页面加载
        WebDriverWait(self.driver, 1).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, "//body[@class='completebody dzKsres hasbgpic hasHeader']"))
        )

        try:
            ans_button = self.driver.find_element(By.XPATH, "//*[@id='check_jx_btn']")
            self.click(ans_button)
            logger.info("获取答案")
            ans_root = self.driver.find_element(By.XPATH, "//*[@id='divAnswer']/div[1]")
            ans_divs = ans_root.find_elements(By.XPATH, "./div")

            for index in range(1, 26):
                topic = ans_divs[index].get_attribute("topic")
                ans_temp = ans_divs[index].find_elements(By.XPATH, "./div[2]/div/div")
                if len(ans_temp) == 2:
                    ans_radio_4[topic] = 0
                else:
                    ans_radio_4[topic] = ord(ans_temp[2].find_element(By.XPATH, "./div").text[0]) - ord('A')
            logger.info("获取四选一单选题答案完成")

            for index in range(26, 31):
                topic = ans_divs[index].get_attribute("topic")
                ans_temp = ans_divs[index].find_elements(By.XPATH, "./div[2]/div/div")
                ans_checkbox_4[topic] = []
                if len(ans_temp) == 2:
                    ans_checkbox_4[topic] = [0]
                else:
                    ans_texts = ans_temp[2].find_element(By.XPATH, "./div").text.split("┋")
                    for text in ans_texts:
                        ans_checkbox_4[topic].append(ord(text[0]) - ord('A'))
            logger.info("获取不定项多选题答案完成")

            for index in range(31, 41):
                topic = ans_divs[index].get_attribute("topic")
                ans_temp = ans_divs[index].find_elements(By.XPATH, "./div[2]/div/div")
                if len(ans_temp) == 2:
                    ans_radio_2[topic] = 0
                else:
                    ans_radio_2[topic] = 1
            logger.info("获取判断题答案完成")

            return ans_radio_4, ans_checkbox_4, ans_radio_2

        except Exception as e:
            logger.warning(f"未获取答案:{e}")
            return False

    def fill_questionnaire(self, survey_url, ACT, ACR4, ACC4, ACR2):
        """填写问卷"""
        try:
            logger.info(f"开始填写40道题的问卷")

            # 打开问卷
            self.driver.get(survey_url)
            logger.info("问卷页面已打开")
            self.wait()

            # 等待页面加载
            # WebDriverWait(self.driver, 1).until(
            #     expected_conditions.presence_of_element_located((By.TAG_NAME, "body"))
            # )

            # 开始问卷
            self.start_questionnaire()

            # 获取题目元素
            t_e, (r4_t, r4_e), (c4_t, c4_e), (r2_t, r2_e) = self.find_question_elements()

            # 填写填空
            for index in range(0, 2):
                logger.info(f"正在填写填空 {index + 1}")
                self.type(t_e[index], ACT[index])
                self.wait()

            self.go_to_next_page()

            # 填写25道四选一单选题
            for index in range(0, 25):
                logger.info(f"正在填写四选一单选题 {index + 1}/25 (题号: {r4_t[index]})")
                # self.click(r4_e[index][ACR4[index]])
                self.click(r4_e[index][ACR4[r4_t[index]]])
                self.wait()
                self.go_to_next_page()

            # 填写5道不定项多选题
            for index in range(0, 5):
                logger.info(f"正在填写不定项多选题 {index + 1}/5 (题号: {c4_t[index]})")
                # for value in ACC4[index]:
                for value in ACC4[c4_t[index]]:
                    self.click(c4_e[index][value])
                self.wait()
                self.go_to_next_page()

            # 填写10道判断题
            for index in range(0, 10):
                logger.info(f"正在填写判断题 {index + 1}/10 (题号: {r2_t[index]})")
                # self.click(r2_e[index][ACR2[index]])
                self.click(r2_e[index][ACR2[r2_t[index]]])
                self.wait()
                self.go_to_next_page()

            logger.info(f"题目填写完成")


        except Exception as e:
            logger.error(f"问卷填写过程出错: {e}")
            self.driver.save_screenshot('error.png')
            return False

    def close(self):
        """关闭浏览器"""
        self.driver.quit()
        logger.info("浏览器已关闭")


class AnswerStorage:
    """获取和使用答案 """

    def __init__(self, path, ans_r4 = None, ans_c4 = None, ans_r2 = None):
        self.path = path
        if ans_r4 is None and ans_c4 is None and ans_r2 is None:
            self.ans_radio_4, self.ans_checkbox_4, self.ans_radio_2 = self.get_answers_from_json()
        else:
            ans_r4_0, ans_c4_0, ans_r2_0 = self.get_answers_from_json()
            self.ans_radio_4, self.ans_checkbox_4, self.ans_radio_2 = self.integrate_answers(
                ans_r4_0, ans_c4_0, ans_r2_0, ans_r4, ans_c4, ans_r2)
            self.save_answers(self.ans_radio_4, self.ans_checkbox_4, self.ans_radio_2)

    def save_answers(self, ans_r4, ans_c4, ans_r2):
        """保存答案到本地文件"""
        answers = {
            "ans_radio_4": ans_r4,
            "ans_checkbox_4": ans_c4,
            "ans_radio_2": ans_r2
        }

        # 保存为 JSON 文件
        import json
        with open(self.path, 'w', encoding = 'utf-8') as f:
            json.dump(answers, f, ensure_ascii = False, indent = 4)
        logger.info(f"答案已保存到 {self.path} 文件")

    def get_answers_from_json(self):
        """从本地文件加载答案"""
        import json
        try:
            with open(self.path, 'r', encoding = 'utf-8') as f:
                answers = json.load(f)
            logger.info("答案已从 answers.json 文件加载")
            return answers.get("ans_radio_4", {}), answers.get("ans_checkbox_4", {}), answers.get("ans_radio_2", {})
        except FileNotFoundError:
            logger.warning("未找到 answers.json 文件，无法加载答案")
            return {}, {}, {}

    def get_answers(self):
        """获取当前存储的答案"""
        return self.ans_radio_4, self.ans_checkbox_4, self.ans_radio_2

    @staticmethod
    def sort_answers(ans_r4, ans_c4, ans_r2):
        """对答案进行排序"""
        ans_r4_sorted = dict(sorted(ans_r4.items(), key = lambda item: int(item[0])))
        ans_c4_sorted = dict(sorted(ans_c4.items(), key = lambda item: int(item[0])))
        ans_r2_sorted = dict(sorted(ans_r2.items(), key = lambda item: int(item[0])))
        return ans_r4_sorted, ans_c4_sorted, ans_r2_sorted

    def integrate_answers(self, ans_r4_0, ans_c4_0, ans_r2_0, ans_r4_1, ans_c4_1, ans_r2_1):
        """整合两个答案集"""
        ans_r4_integrated = {**ans_r4_0, **ans_r4_1}
        ans_c4_integrated = {**ans_c4_0, **ans_c4_1}
        ans_r2_integrated = {**ans_r2_0, **ans_r2_1}

        return self.sort_answers(ans_r4_integrated, ans_c4_integrated, ans_r2_integrated)


def main():
    # from ans0_config import SURVEY_URL, ANSWERS_CONFIG_TEXTAREA, ANSWERS_CONFIG_RADIO_4, ANSWERS_CONFIG_CHECKBOX_4, \
    #     ANSWERS_CONFIG_RADIO_2, BROWSER_CONFIG
    filler = AutoFiller(headless = False)
    try:
        # filler.fill_questionnaire(SURVEY_URL, ANSWERS_CONFIG_TEXTAREA, ANSWERS_CONFIG_RADIO_4,
        #                           ANSWERS_CONFIG_CHECKBOX_4, ANSWERS_CONFIG_RADIO_2)
        storage = AnswerStorage('answers.json')
        ans_radio_4, ans_checkbox_4, ans_radio_2 = storage.get_answers()
        filler.fill_questionnaire("https://www.wjx.cn/vm/ONW26bZ.aspx",["0", "00000000"], ans_radio_4,
                                  ans_checkbox_4, ans_radio_2)

        import time
        time.sleep(1000)

        # # 获取答案
        # ans = filler.get_ans()
        # if ans:
        #     ans_r4, ans_c4, ans_r2 = ans
        #     storage = AnswerStorage('answers.json', ans_r4, ans_c4, ans_r2)
        #     ans_r4_s, ans_c4_s, ans_r2_s = storage.get_answers()
        # else:
        #     logger.warning("未获取到答案，跳过保存步骤")
        #     raise Exception("未获取到答案")

    except Exception as e:
        logger.error(f"程序运行出错: {e}")

    finally:
        filler.close()


if __name__ == "__main__":
    main()
