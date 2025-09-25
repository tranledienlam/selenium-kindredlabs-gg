
import argparse
from selenium_browserkit import BrowserManager, Node, Utility, By

from googl import Setup as GoogleSetup, Auto as GoogleAuto

PROJECT_URL = "https://waitlist.kindredlabs.ai?code=D8741E8"

class Setup:
    def __init__(self, node: Node, profile) -> None:
        self.node = node
        self.profile = profile
        self.google_setup = GoogleSetup(node, profile)
        
        self.run()

    def run(self):
        self.google_setup._run()
        self.node.new_tab(f'{PROJECT_URL}', method="get")

class Auto:
    def __init__(self, node: Node, profile: dict) -> None:
        self.node = node
        self.profile_name = profile.get('profile_name')
        self.email = profile.get('email')
        self.pwd_email = profile.get('pwd_email')
        self.google_auto = GoogleAuto(node, profile)
        self.completed = []

        self.run()

    def loaded(self):
        for i in range(1,3):
            if not self.node.find(By.TAG_NAME, 'main'):
                if i < 2:
                    self.node.log(f'Thử reload lại')
                    self.node.reload_tab()
                    continue
                return False
            return True
        
    def is_login(self):
        if not self.loaded():
            return
        self.node.scroll_to_position(position='middle')
        span_all = self.node.find_all(By.TAG_NAME, 'span')
        for span in span_all:
            if 'log in' in span.text.lower():
                self.node.log(f'Cần đăng nhập')
                return False
            elif 'log out' in span.text.lower():
                url = self.node.get_url()
                if 'dashboard' not in url:
                    self.node.go_to('https://waitlist.kindredlabs.ai/dashboard')
                    self.loaded()
                point = self.node.get_text(By.CSS_SELECTOR, '.text-7xl')
                self.node.log(f'Đã đăng nhập thành công')
                self.completed.append(f'point: {point}')
                return True
        
        return None
    
    def active_login(self):
        for _ in range(2):
            loged_in = self.is_login()
            if loged_in == True:
                return True
            elif loged_in == False:
                btn_gg = self.node.find(By.XPATH, '//div[@id="login-btn"]//button[1]')
                self.node.scroll_to_element(btn_gg)
                self.node.click(btn_gg)
                self.google_auto.confirm_login()
                toast_success = self.node.find(By.CSS_SELECTOR, '[data-type="success"]', timeout=60)
                if not toast_success:
                    return False
                self.node.wait_for_disappear(By.CSS_SELECTOR, '[data-type="success"]')
            else:
                return None

        return None
    
    def task_social(self):
        timeout = Utility.timeout(600)
        while True:
            btn_claimed = 0
            btns = self.node.find_all(By.XPATH, '//section[.//p[contains(text(), "social mission")]]//button')
            for btn in btns:
                if btn.get_attribute("disabled") is not None:
                    if 'loading' in btn.text.lower():
                        self.node.find_and_click(By.XPATH, '//section[.//p[contains(text(), "social mission")]]//b[contains(text(), "Claim reward")]')
                        break
                    else:
                        btn_claimed += 1
                else:
                    parent = self.node.find(By.XPATH, './..', btn)
                    self.node.scroll_to_element(btn)
                    name_tag = parent.tag_name
                    if name_tag == 'a':
                        href = parent.get_attribute('href')
                        self.node.click(btn)
                        self.node.close_tab(href)
                    else:
                        self.node.click(btn)
                    break
            if len(btns) == btn_claimed:
                self.completed.append('Social')
                return True

    def task_checkin(self):
        btns = self.node.find_all(By.XPATH, '//button/span')
        for btn in btns:
            if 'claim reward' in btn.text.lower():
                self.node.scroll_to_element(btn)
                self.node.click(btn)
                popup = self.node.find(By.CSS_SELECTOR, '[role="dialog"]')
                if popup:
                    self.node.find_and_click(By.XPATH, './/button', popup)
                self.completed.append('check-in')
                return True

    def run(self):
        if not self.google_auto:
            self.node.log(f'Đăng nhập goggle khôgn thành công')
            pass

        self.node.new_tab(f'{PROJECT_URL}', method="get")
        if not self.active_login():
            return
        self.task_social()
        self.task_checkin()
        self.node.snapshot(f'Hoàn thành: {self.completed}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto', action='store_true', help="Chạy ở chế độ tự động")
    parser.add_argument('--headless', action='store_true', help="Chạy trình duyệt ẩn")
    parser.add_argument('--disable-gpu', action='store_true', help="Tắt GPU")
    args = parser.parse_args()

    profiles = Utility.read_data('profile_name', 'email', 'pwd_email')
    max_profiles = Utility.read_config('MAX_PROFLIES')

    browser_manager = BrowserManager(auto_handler=Auto, setup_handler=Setup)
    browser_manager.update_config(
                        headless=args.headless, 
                        disable_gpu=args.disable_gpu, 
                        use_tele=True
                    )
    browser_manager.run_menu(
        profiles=profiles,
        max_concurrent_profiles=max_profiles,
        auto=args.auto
    )