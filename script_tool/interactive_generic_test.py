import time
import tkinter as tk
from tkinter import messagebox, scrolledtext
from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, \
    InvalidArgumentException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def create_browser_obj():
    option = webdriver.ChromeOptions()
    option.add_argument('--disable-gpu')
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    option.add_experimental_option('useAutomationExtension', False)
    option.add_argument('--hide-scrollbars')
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.14 Safari/537.36'
    option.add_argument(f'user-agent={user_agent}')
    option.add_argument("--window-size=1920,1080")
    browser = webdriver.Chrome(options=option)
    browser.maximize_window()
    browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
    })
    return browser


class GenericTester:
    def __init__(self, browser, output_widget):
        self.browser = browser
        self.output_widget = output_widget

    def perform_action(self, by, locator, action, attribute=None, delay=3, find_multiple=True, send_keys_text=None):
        try:
            elements = self.browser.find_elements(by, locator)
            self.output_widget.insert(tk.END, f"定位到 {len(elements)} 个元素: {locator} 使用 {by}\n")
            logger.info(f"定位到 {len(elements)} 个元素: {locator} 使用 {by}\n")
            if not find_multiple:
                elements = elements[:1]
                self.output_widget.insert(tk.END, f"截取第 1 个元素: {locator} 使用 {by}\n")
                logger.info(f"截取第 1 个元素: {locator} 使用 {by}\n")

            for element in elements:
                self.output_widget.insert(tk.END, f"对元素执行操作: {action}\n")
                logger.info(f"对元素执行操作: {action}\n")

                if action == "click":
                    element.click()
                elif action == "print_text":
                    self.output_widget.insert(tk.END, element.text + "\n")
                elif action == "print_attribute" and attribute:
                    self.output_widget.insert(tk.END, element.get_attribute(attribute) + "\n")
                elif action == "print_count":
                    self.output_widget.insert(tk.END, str(len(elements)) + "\n")
                elif action == "highlight":
                    self.highlight_element(element)
                elif action == "clear":
                    element.clear()
                elif action == "send_keys":
                    if send_keys_text:
                        element.clear()
                        element.send_keys(send_keys_text)
                        self.output_widget.insert(tk.END, f"已输入: {send_keys_text}\n")
                    else:
                        self.output_widget.insert(tk.END, "send_keys 需要输入文本.\n")
                elif action == "send_keys&enter":
                    if send_keys_text:
                        element.clear()
                        element.send_keys(send_keys_text + Keys.RETURN)
                        self.output_widget.insert(tk.END, f"已输入: {send_keys_text}\n")
                    else:
                        self.output_widget.insert(tk.END, "send_keys 需要输入文本.\n")
                else:
                    self.output_widget.insert(tk.END, f"未知的行为: {action}\n")
                    logger.warning(f"未知的行为: {action}\n")

                time.sleep(delay)

        except NoSuchElementException:
            self.output_widget.insert(tk.END, f"元素未找到: {locator}\n")
            logger.error(f"元素未找到: {locator}\n")
        except ElementClickInterceptedException:
            self.output_widget.insert(tk.END, f"元素无法点击: {locator}\n")
            logger.error(f"元素无法点击: {locator}\n")
        except Exception as e:
            self.output_widget.insert(tk.END, f"其它错误: {str(e)}\n")
            logger.error(f"其它错误: {str(e)}\n")

    def highlight_element(self, element):
        self.browser.execute_script("arguments[0].style.border='3px solid red'", element)


def start_testing():
    url = entry_url.get()
    logger.info(f"用户输入 URL: {url}")
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    try:
        browser.get(url)
        success_msg = "浏览器已导航到指定网址.\n"
        output_text.insert(tk.END, success_msg)
        logger.info(success_msg)
    except InvalidArgumentException as e:
        error_msg = f"无效的 URL: {url}\n{e}\n"
        output_text.insert(tk.END, error_msg)
        logger.error(error_msg)


def perform_test_action():
    locator = entry_locator.get()
    action = action_var.get()
    by = by_var.get()
    delay = float(entry_delay.get())
    find_multiple = find_multiple_var.get()
    attribute = entry_attribute.get() if action == "print_attribute" else None
    send_keys_text = entry_send_keys.get() if action in ["send_keys", "send_keys&enter"] else None

    # 清空输出框
    output_text.delete(1.0, tk.END)

    logger.info(f"用户选择 By: {by}")
    logger.info(f"用户输入 Locator: {locator}")
    logger.info(f"用户选择 Action: {action}")
    if attribute:
        logger.info(f"用户输入 Attribute: {attribute}")
    logger.info(f"用户输入 Delay: {delay}")
    logger.info(f"用户选择 find_multiple: {find_multiple}")
    if send_keys_text:
        logger.info(f"用户输入 send_keys_text: {send_keys_text}")

    by_mappings = {
        'ID': By.ID,
        'CLASS_NAME': By.CLASS_NAME,
        'CSS_SELECTOR': By.CSS_SELECTOR,
        'LINK_TEXT': By.LINK_TEXT,
        'XPATH': By.XPATH
    }

    tester.perform_action(by_mappings[by], locator, action, attribute, delay, find_multiple, send_keys_text)


def quit_program():
    browser.quit()
    root.quit()
    logger.info("用户退出程序")

if __name__ == '__main__':
    browser = create_browser_obj()
    root = tk.Tk()
    root.title("通用测试工具")

    tk.Label(root, text="网址 URL:").grid(row=0, column=0, padx=5, pady=5)
    entry_url = tk.Entry(root, width=50)
    entry_url.grid(row=0, column=1, padx=5, pady=5)
    tk.Button(root, text="开始测试", command=start_testing).grid(row=0, column=2, padx=5, pady=5)

    tk.Label(root, text="Locator:").grid(row=1, column=0, padx=5, pady=5)
    entry_locator = tk.Entry(root, width=50)
    entry_locator.grid(row=1, column=1, padx=5, pady=5)

    # 添加 By 方法选择
    by_var = tk.StringVar()
    by_var.set("XPATH")
    tk.OptionMenu(root, by_var, "ID", "CLASS_NAME", "CSS_SELECTOR", "LINK_TEXT", "XPATH").grid(row=1, column=2, padx=5,
                                                                                               pady=5)

    tk.Label(root, text="Delay (秒):").grid(row=2, column=0, padx=5, pady=5)
    entry_delay = tk.Entry(root, width=10)
    entry_delay.grid(row=2, column=1, padx=5, pady=5)
    entry_delay.insert(0, "3")

    action_var = tk.StringVar()
    action_var.set("click")
    tk.OptionMenu(root, action_var, "click", "print_text", "print_attribute", "print_count", "highlight", "clear",
                  "send_keys", "send_keys&enter").grid(row=3, column=1, padx=5, pady=5)

    tk.Label(root, text="属性名 (仅 print_attribute):").grid(row=4, column=0, padx=5, pady=5)
    entry_attribute = tk.Entry(root, width=50)
    entry_attribute.grid(row=4, column=1, padx=5, pady=5)

    tk.Label(root, text="输入文本 (仅 send_keys):").grid(row=5, column=0, padx=5, pady=5)
    entry_send_keys = tk.Entry(root, width=50)
    entry_send_keys.grid(row=5, column=1, padx=5, pady=5)

    # 添加单选按钮以选择 find_element 或 find_elements
    find_multiple_var = tk.BooleanVar()
    find_multiple_var.set(True)
    tk.Checkbutton(root, text="定位多个", var=find_multiple_var).grid(row=6, column=1, padx=5, pady=5)

    tk.Button(root, text="执行操作", command=perform_test_action).grid(row=7, column=1, padx=5, pady=5)

    # 更新：增加退出按钮
    tk.Button(root, text="退出", command=quit_program).grid(row=0, column=3, padx=5, pady=5)

    # 更新：增加输出框
    output_text = scrolledtext.ScrolledText(root, width=80, height=20)
    output_text.grid(row=8, column=0, columnspan=4, padx=5, pady=5)

    tester = GenericTester(browser, output_text)

    root.mainloop()