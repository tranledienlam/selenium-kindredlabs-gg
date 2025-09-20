#version browser_automation 04/04/2025
import argparse

from selenium_browserkit import BrowserManager, Node, Utility, By

class Setup:
    def __init__(self, node: Node, profile) -> None:
        self.node = node
        self.profile = profile
        
    def _run(self):
        # Kiểm tra đăng nhập Google
        self.node.go_to('https://accounts.google.com/signin')

class Auto:
    def __init__(self, node: Node, profile: dict) -> None:
        self.driver = node._driver
        self.node = node
        self.profile_name = profile.get('profile_name')
        self.email = profile.get('email')
        self.pwd_email = profile.get('pwd_email')

        self.run()
        
    def read_code(self, title: str, xpath_code: str):
        current_tab = self.driver.current_window_handle
        if not self.node.switch_tab('https://mail.google.com'):
            self.node.new_tab('https://mail.google.com')
        timeout = Utility.timeout(60)
        while timeout():
            el_msg = self.node.find(By.XPATH, f'((//table[@role="grid"])[1]//tr[1]//span[@name="{title}"])[last()]')
            if el_msg:
                self.node.click(el_msg)
                code = self.node.get_text(By.XPATH, xpath_code)
                if code:
                    self.driver.switch_to.window(current_tab)
                    return code
                else:
                    self.node.snapshot('Tìm thấy mail, nhưng không thể lấy code', stop=False)
                    self.driver.switch_to.window(current_tab)
                    
                    return None
            else:
                Utility.wait_time(5)
                self.node.reload_tab()
        self.driver.switch_to.window(current_tab)
        return None
    def confirm_login(self):
        confirmed = False
        try:
            current_window = self.driver.current_window_handle

            if self.node.switch_tab('https://accounts.google.com'):
                url_google = self.node.get_url()
                if url_google:
                    if 'auth' in url_google:
                        if self.node.find_and_click(By.CSS_SELECTOR, f'[data-email="{self.email}"]'):
                            confirmed = True
                    elif 'signin' in url_google:
                        self.node.log(f'Cần đăng nhập google trước')
                        self.node.close_tab()
                else:
                    self.node.log(f'Khôgn thể lấy url google')
            self.driver.switch_to.window(current_window)
        except Exception as e:
            self.node.log(f'Bị lỗi khi confirm đăng nhập google: {e}')

        return confirmed
    def run(self):
        '''Thực hiện đăng nhập tài khảon Google'''
        if not self.email:
            self.node.snapshot(f'Không tồn tại thông tin email trong data.txt', stop=False)
            return

        self.node.go_to('https://accounts.google.com/signin')
        
        # Đợi và kiểm tra xem đã đăng nhập chưa bằng cách tìm avatar hoặc email hiển thị
        if self.node.find(By.CSS_SELECTOR, '[aria-label*="@gmail.com"]'):
            self.node.log('✅ Đã đăng nhập Google')
            return True
            
        # Nếu chưa đăng nhập, thực hiện đăng nhập
        self.node.log('⚠️ Chưa đăng nhập Google, đang thực hiện đăng nhập...')
        if not self.pwd_email:
            self.node.snapshot(f'Không tồn tại mật khẩu email trong data.txt', stop=False)
            return
        
        # Nhập email
        if not self.node.find_and_input(By.CSS_SELECTOR, 'input[type="email"]', self.email, None, 0.1):
            self.node.snapshot('Không tìm thấy ô nhập email', stop=False)
            return
            
        # Click nút Next
        if not self.node.press_key('Enter'):
            self.node.snapshot('Không thể nhấn nút Enter', stop=False)
            return
            
        # Đợi và nhập mật khẩu
        if not self.node.find_and_input(By.CSS_SELECTOR, 'input[type="password"]', self.pwd_email, None, 0.1):
            self.node.snapshot('Không tìm thấy ô nhập mật khẩu', stop=False)
            return
            
        # Click nút Next
        if not self.node.press_key('Enter'):
            self.node.snapshot('Không thể nhấn nút Enter', stop=False)
            return
        
        # Thỉnh thoảng nó sẽ hỏi đoạn này passkeys
        if self.node.find(By.XPATH, '//div[text()="With passkeys, your device will simply ask you for your Windows PIN or biometric and let Google know it\'s really you signing in"]', timeout=15):
            self.node.log('🔄 Đang thực hiện xác thực bằng passkey...')
            if not self.node.find_and_click(By.XPATH, '//span[text()="Not now"]'):
                self.node.snapshot('Không tìm thấy nút "Skip"', stop=False)
                return
            self.node.find_and_click(By.XPATH, '//span[text()="Cancel"]')
        # Đợi và kiểm tra đăng nhập thành công
        if self.node.find(By.CSS_SELECTOR, '[aria-label*="@gmail.com"]'):
            self.node.log('✅ Đăng nhập Google thành công')
        else:
            self.node.snapshot('Không thể xác nhận đăng nhập thành công', stop=False)
            return
        
        return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto', action='store_true', help="Chạy ở chế độ tự động")
    parser.add_argument('--headless', action='store_true', help="Chạy trình duyệt ẩn")
    parser.add_argument('--disable-gpu', action='store_true', help="Tắt GPU")
    args = parser.parse_args()

    profiles = Utility.read_data('profile_name', 'email', 'pwd_email')
    max_profiles = Utility._read_config('MAX_PROFLIES')

    browser_manager = BrowserManager(auto_handler=Auto, setup_handler=Setup)
    browser_manager.update_config(headless=args.headless, disable_gpu=args.disable_gpu)
    browser_manager.add_extensions('Meta-Wallet-*.crx','OKX-Wallet-*.crx')
    browser_manager.run_menu(
        profiles=profiles,
        max_concurrent_profiles=max_profiles,
        auto=args.auto
    )