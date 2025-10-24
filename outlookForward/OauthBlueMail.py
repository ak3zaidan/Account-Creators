from bs4 import BeautifulSoup
import urllib.parse
import requests
import time
import re

SHOULD_LOG = False

class SimpleLogger:
    def __init__(self, log_file=None):
        self.log_file = log_file if SHOULD_LOG else None
        if self.log_file:
            # 确保logs目录存在
            import os
            if not os.path.exists('logs'):
                os.makedirs('logs')
            self.log_path = os.path.join('logs', self.log_file)
    
    def _log(self, prefix, message):
        """只记录到文件，不再控制台输出"""
        if not SHOULD_LOG:
            return
            
        import time
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            print(f"[{timestamp}] [{prefix}] {message}\n")
        except Exception:
            pass # 安静地忽略写入错误
    
    def debug(self, message): 
        self._log("DEBUG", message)
    
    def info(self, message): 
        self._log("INFO", message)
    
    def success(self, message): 
        self._log("SUCCESS", message)
    
    def warning(self, message): 
        self._log("WARNING", message)
    
    def error(self, message): 
        self._log("ERROR", message)
    
    def critical(self, message): 
        self._log("CRITICAL", message)

logger = SimpleLogger()

class BlueMailOAuthClient:
    CLIENT_ID = "8b4ba9dd-3ea5-4e5f-86f1-ddba2230dcf2"
    REDIRECT_URI = "me.bluemail.mail://auth"
    SCOPES = [
        "openid", "profile", "email", "offline_access",
        "MailboxSettings.ReadWrite",
        "Mail.ReadWrite"
    ]
    
    def __init__(self, email, password):
        """
        初始化OAuth客户端
        
        参数:
            email (str): Microsoft账号邮箱
            password (str): Microsoft账号密码
        """
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.proxy = None
        
        # 配置会话 - 使用Edge浏览器的UA，模拟原始可执行文件
        self.session.headers.update({
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'sec-ch-ua': '"Microsoft Edge";v="122", "Chromium";v="122", "Not(A:Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        })
        
        # 保存授权流程中的关键数据
        self.auth_data = {
            "refresh_token": None,
            "flow_trace": []
        }
        
        # 授权流程中的调试信息
        self.debug_info = {
            "response_lengths": [],
            "urls_visited": [],
            "form_data": []
        }
    
    def set_proxy(self, proxy):
        if not proxy or not proxy.strip():
            logger.info("未提供代理地址，将使用直连方式")
            self.proxy = None
            return False
            
        try:
            # 格式化代理地址
            proxy_dict = {
                "http": proxy,
                "https": proxy
            }
            
            # 更新会话的代理设置
            self.session.proxies.update(proxy_dict)
            # 启用信任环境
            self.session.trust_env = True
            
            # 保存代理信息
            self.proxy = proxy
            
            logger.info(f"已设置代理: {proxy}")
            return True
        except Exception as e:
            logger.error(f"设置代理时出错: {str(e)}")
            self.proxy = None
            return False
    
    def _add_to_trace(self, step_name, request_url, response=None):
        """添加步骤到流程追踪"""
        status_code = None
        if response and hasattr(response, "status_code"):
            status_code = response.status_code
            
        self.auth_data["flow_trace"].append({
            "step": step_name,
            "url": request_url,
            "status_code": status_code,
            "timestamp": time.time()
        })
    
    def _build_auth_url(self):
        """构建初始授权URL"""
        params = {
            "client_id": self.CLIENT_ID,
            "response_type": "code",
            "redirect_uri": self.REDIRECT_URI,
            "scope": " ".join(self.SCOPES),
            "prompt": "login",
            "login_hint": self.email,
            "client-request-id": f"{self._generate_request_id()}",
            "x-client-SKU": "MSAL.JS",
            "x-client-Ver": "1.4.4"
        }
        return f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?{urllib.parse.urlencode(params)}"
    
    def _generate_request_id(self):
        """生成请求ID，类似于真实客户端的请求ID格式"""
        import uuid
        return str(uuid.uuid4()).replace('-', '')
    
    def execute_auth_flow(self, max_retries=10):
        """
        执行完整授权流程，支持重试
        
        参数:
            max_retries (int): 最大重试次数，默认为10次
            
        返回:
            str: 成功时返回刷新令牌，失败时返回None
        """
        for retry_count in range(max_retries):
            try:
                if retry_count == 0:
                    if self.proxy:
                        logger.info(f"开始执行Microsoft OAuth授权流程 (使用代理: {self.proxy})")
                    else:
                        logger.info("开始执行Microsoft OAuth授权流程 (直连模式)")
                else:
                    logger.info(f"第{retry_count+1}/{max_retries}次重试Microsoft OAuth授权流程")
                
                # 配置代理
                if self.proxy:
                    # 格式化代理地址
                    proxy_dict = {
                        "http": self.proxy,
                        "https": self.proxy
                    }
                    # 更新会话的代理设置
                    self.session.proxies.update(proxy_dict)
                    # 启用信任环境
                    self.session.trust_env = True
                else:
                    # 如果没有代理，则使用直连
                    self.session.proxies.clear()
                    self.session.trust_env = False
                
                # 每次重试使用新的会话
                if retry_count > 0:
                    self.session = requests.Session()
                    self.session.headers.update({
                        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-User': '?1',
                        'Sec-Fetch-Dest': 'document',
                        'sec-ch-ua': '"Microsoft Edge";v="122", "Chromium";v="122", "Not(A:Brand";v="24"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"'
                    })
                    
                    # 重新应用代理设置
                    if self.proxy:
                        proxy_dict = {
                            "http": self.proxy,
                            "https": self.proxy
                        }
                        self.session.proxies.update(proxy_dict)
                        self.session.trust_env = True
                
                # 步骤1: 构建初始授权URL并请求
                auth_url = self._build_auth_url()
                logger.info(f"步骤1: 初始授权请求 URL: {auth_url}")
                
                # 发送请求
                ret = self.session.get(auth_url)
                logger.info(f"授权页面请求状态码: {ret.status_code}")
                
                # 从ServerData变量中提取登录URL
                login_url = self._extract_server_data_value(ret.text, 'urlPost')
                if not login_url:
                    login_url = self._extract_server_data_value(ret.text, 'urlLogin')
                
                if not login_url:
                    # 备用方法：尝试直接从HTML中提取form的action属性
                    login_url = self._extract_form_action(ret.text)
                    
                if not login_url:
                    logger.error("无法提取登录URL，登录流程失败")
                    if retry_count < max_retries - 1:
                        logger.warning(f"等待3秒后继续第{retry_count+2}次尝试")
                        time.sleep(3)
                    continue
                
                logger.info(f"提取到登录URL: {login_url}")
                
                # 提取PPFT令牌（这是表单提交必需的）
                ppft = self._extract_ppft(ret.text)
                if not ppft:
                    logger.error("无法提取PPFT令牌，登录流程失败")
                    if retry_count < max_retries - 1:
                        logger.warning(f"等待3秒后继续第{retry_count+2}次尝试")
                        time.sleep(3)
                    continue
                
                logger.info(f"提取到PPFT令牌: {ppft[:20]}...")
                
                # 构建登录数据
                login_data = {
                    'login': self.email,
                    'loginfmt': self.email,
                    'passwd': self.password,
                    'PPFT': ppft,
                    'PPSX': 'PassportR',
                    'LoginOptions': 3,
                    'type': 11,
                    'NewUser': 1,
                    'KMSI': 1  # 保持登录
                }
                
                # 从HTML中提取其他隐藏字段
                hidden_fields = self._extract_hidden_fields(ret.text)
                for name, value in hidden_fields.items():
                    if name != 'PPFT':  # 不覆盖PPFT
                        login_data[name] = value
                
                # 设置登录请求头
                login_headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Origin': self._get_origin(login_url),
                    'Referer': auth_url
                }
                
                # 提交登录表单 - 关闭自动重定向以便分析响应
                logger.info("提交登录请求...")
                login_response = self.session.post(login_url, data=login_data, headers=login_headers, allow_redirects=False)
                logger.info(f"登录请求状态码: {login_response.status_code}")
                
                # 检查是否有错误消息
                error_message = self._extract_error_message(login_response.text)
                if error_message:
                    logger.error(f"登录失败: {error_message}")
                    if retry_count < max_retries - 1:
                        logger.warning(f"等待3秒后继续第{retry_count+2}次尝试")
                        time.sleep(3)
                    continue
                logger.info("LLOGIN RESPONSE URL: " + login_response.url)
                logger.info(f"登录响应长度: {login_response.text} 字符")
                # 处理重定向 - 获取授权码或处理同意页面
                if login_response.status_code in [302, 303]:
                    location = login_response.headers.get('Location')
                    logger.info(f"登录后重定向到: {location}")
                    
                    # 检查是否直接获取到授权码
                    if 'code=' in location:
                        auth_code = self._extract_auth_code(location)
                        logger.info(f"直接获取到授权码: {auth_code[:15]}...")
                        
                        # 使用授权码获取刷新令牌
                        refresh_token = self._get_token_from_code(auth_code)
                        if refresh_token:
                            return refresh_token
                        else:
                            logger.error("使用授权码获取刷新令牌失败")
                            if retry_count < max_retries - 1:
                                logger.warning(f"等待3秒后继续第{retry_count+2}次尝试")
                                time.sleep(3)
                            continue
                    
                    # 检查是否重定向到同意页面
                    if 'consent' in location.lower():
                        logger.info("重定向到同意页面，处理同意流程...")
                        consent_response = self.session.get(location, allow_redirects=False)
                        auth_code = self._handle_consent(consent_response)
                        
                        if auth_code:
                            refresh_token = self._get_token_from_code(auth_code)
                            if refresh_token:
                                return refresh_token
                            else:
                                logger.error("使用授权码获取刷新令牌失败")
                                if retry_count < max_retries - 1:
                                    logger.warning(f"等待3秒后继续第{retry_count+2}次尝试")
                                    time.sleep(3)
                                continue
                    
                    # 其他重定向，继续跟踪
                    logger.info("跟随重定向...")
                    refresh_token = self._follow_redirects(location)
                    if refresh_token:
                        return refresh_token
                    else:
                        logger.error("跟随重定向未获取到刷新令牌")
                        if retry_count < max_retries - 1:
                            logger.warning(f"等待3秒后继续第{retry_count+2}次尝试")
                            time.sleep(3)
                        continue
                
                # 如果状态码是200，检查是否是同意页面
                if 'consent' in login_response.text.lower() or "https://account.live.com/proofs/Add" in login_response.text:
                    logger.info("响应包含同意页面，处理同意流程...")
                    auth_code = self._handle_consent(login_response)
                    
                    if auth_code:
                        refresh_token = self._get_token_from_code(auth_code)
                        if refresh_token:
                            return refresh_token
                        else:
                            logger.error("使用授权码获取刷新令牌失败")
                            if retry_count < max_retries - 1:
                                logger.warning(f"等待3秒后继续第{retry_count+2}次尝试")
                                time.sleep(3)
                            continue
                
                logger.error("登录流程未获取到授权码")
                if retry_count < max_retries - 1:
                    logger.warning(f"等待3秒后继续第{retry_count+2}次尝试")
                    time.sleep(3)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"网络请求异常: {str(e)}")
                if retry_count < max_retries - 1:
                    logger.warning(f"等待3秒后继续第{retry_count+2}次尝试")
                    time.sleep(3)
            except Exception as e:
                logger.error(f"登录过程发生异常: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                if retry_count < max_retries - 1:
                    logger.warning(f"等待3秒后继续第{retry_count+2}次尝试")
                    time.sleep(3)
        
        # 所有重试都失败
        logger.error(f"OAuth授权流程失败，已尝试{max_retries}次")
        return None
    
    def _extract_server_data_value(self, html, key):
        """从ServerData JavaScript变量中提取值"""
        try:
            # 查找ServerData变量定义
            server_data_match = re.search(r'var\s+ServerData\s*=\s*({[^;]+});', html, re.DOTALL)
            if not server_data_match:
                return None
            
            server_data_str = server_data_match.group(1)
            
            # 查找特定键的值
            key_match = re.search(rf'{key}\s*:\s*[\'"]([^\'"]+)[\'"]', server_data_str)
            if key_match:
                return key_match.group(1)
            
            return None
        except Exception as e:
            logger.error(f"提取ServerData值时出错: {str(e)}")
            return None
    
    def _extract_form_action(self, html):
        """从HTML中提取表单的action属性"""
        form_match = re.search(r'<form[^>]*action=[\'"]([^\'"]+)[\'"]', html, re.DOTALL)
        if form_match:
            form_action = form_match.group(1)
            # 确保是完整URL
            if not form_action.startswith('http'):
                if form_action.startswith('/'):
                    form_action = 'https://login.live.com' + form_action
                else:
                    form_action = 'https://login.live.com/' + form_action
            return form_action
        return None
    
    def _extract_ppft(self, html):
        """提取PPFT令牌"""
        # 尝试多种模式提取PPFT
        ppft_patterns = [
            r'name=[\'"]PPFT[\'"][^>]*id=[\'"][^\'"]*[\'"][^>]*value=[\'"]([^\'"]+)[\'"]',
            r'name=[\'"]PPFT[\'"][^>]*value=[\'"]([^\'"]+)[\'"]',
            r'id=[\'"]i0327[\'"][^>]*value=[\'"]([^\'"]+)[\'"]',
            r'id=[\'"]sFT[\'"][^>]*value=[\'"]([^\'"]+)[\'"]'
        ]
        
        for pattern in ppft_patterns:
            match = re.search(pattern, html)
            if match:
                return match.group(1)
        
        # 尝试从ServerData中提取
        ppft = self._extract_server_data_value(html, 'sFTTag')
        if ppft:
            # 从sFTTag HTML片段中提取value属性
            match = re.search(r'value=[\'"]([^\'"]+)[\'"]', ppft)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_hidden_fields(self, html):
        """提取所有隐藏表单字段"""
        hidden_fields = {}
        hidden_inputs = re.findall(r'<input[^>]*type=[\'"]hidden[\'"][^>]*name=[\'"]([^\'"]+)[\'"][^>]*value=[\'"]([^\'"]*)[\'"]', html)
        for name, value in hidden_inputs:
            hidden_fields[name] = value
        return hidden_fields
    
    def _extract_error_message(self, html):
        """提取错误消息"""
        error_patterns = [
            r'id=[\'"]error[^>]*>([^<]+)<',
            r'class=[\'"]error[^>]*>([^<]+)<',
            r'id=[\'"]errorText[^>]*>([^<]+)<',
            r'id=[\'"]errorDescription[\'"][^>]*>([^<]+)<',
            r'error_description=([^&"]+)',
            r'class=[\'"]alert-error[\'"][^>]*>([^<]+)<'
        ]
        
        for pattern in error_patterns:
            match = re.search(pattern, html)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_auth_code(self, url):
        """从URL中提取授权码"""
        # 标准OAuth重定向URL中的授权码
        match = re.search(r'code=([^&]+)', url)
        if match:
            return match.group(1)
        
        # 处理自定义协议URL（me.bluemail.mail://auth/?code=XXX）
        if 'me.bluemail.mail://' in url:
            match = re.search(r'me\.bluemail\.mail://auth/?\?code=([^&]+)', url)
            if match:
                return match.group(1)
        
        return None
    
    def _get_origin(self, url):
        """从URL中提取origin (scheme://host)"""
        parts = url.split('/')
        if len(parts) >= 3:
            return '/'.join(parts[:3])
        return url
    
    def _handle_consent(self, response):
        """处理同意页面"""
        try:
            # 获取响应内容
            consent_html = response.text
            consent_url = response.url
            
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(consent_html, 'html.parser')
            
            # 提取表单的action属性
            form = soup.find('form')
            form_action = form.get('action') if form else None
            
            if form_action:
                # 确保form_action是完整URL
                if not form_action.startswith('http'):
                    if form_action.startswith('/'):
                        base_url = self._get_origin(consent_url)
                        form_action = base_url + form_action
                    else:
                        base_url = self._get_origin(consent_url)
                        form_action = base_url + '/' + form_action
                logger.info(f"同意页面表单URL: {form_action}")
            else:
                # 如果找不到表单action，使用一个默认值
                form_action = "https://account.live.com/Consent/Update"
                logger.info(f"同意页面表单URL（备用方法）: {consent_url}")
            
            # 提取表单中的所有输入字段，保持原始值
            form_data = {}
            if form:
                for input_tag in form.find_all('input'):
                    if input_tag.get('name'):
                        form_data[input_tag.get('name')] = input_tag.get('value', '')
            
            # 显示找到的表单字段名称
            logger.info(f"同意表单数据: {list(form_data.keys())}")
            
            # 添加同意标记，不修改原始的client_id和scope值
            form_data.update({
                'ucaccept': 'Yes',
                'ucAction': '1',  # 这是关键 - 表示接受同意
                'UCAction': '1'
            })
            
            # 设置特定的请求头
            consent_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': self._get_origin(consent_url),
                'Referer': consent_url,
                'Cache-Control': 'max-age=0',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # 提交同意请求，允许重定向但不自动处理自定义协议
            logger.info("提交同意请求，保留原始表单字段值...")
            try:
                # 提交表单但不允许自动重定向，以便能够检查响应头中的Location
                consent_response = self.session.post(form_action, data=form_data, headers=consent_headers, allow_redirects=False)
                
                # 检查是否有重定向
                if consent_response.status_code in [301, 302, 303, 307, 308]:
                    location = consent_response.headers.get('Location')
                    logger.info(f"同意请求重定向到: {location}")
                    
                    # 检查是否重定向到自定义协议URL
                    if location.startswith('me.bluemail.mail://'):
                        logger.info("检测到重定向到自定义协议URL")
                        
                        # 直接从URL中提取授权码
                        auth_code = self._extract_auth_code(location)
                        if auth_code:
                            logger.info(f"从自定义协议URL中提取到授权码: {auth_code[:15]}...")
                            return auth_code
                    
                    # 如果不是自定义协议，手动跟随重定向
                    next_url = location
                    redirect_count = 0
                    max_redirects = 5
                    
                    while redirect_count < max_redirects:
                        logger.info(f"跟随重定向 {redirect_count+1}: {next_url}")
                        
                        # 检查当前URL是否包含授权码
                        if 'code=' in next_url:
                            auth_code = self._extract_auth_code(next_url)
                            logger.info(f"从重定向URL中获取到授权码: {auth_code[:15]}...")
                            return auth_code
                        
                        # 如果是自定义协议URL，直接提取授权码
                        if next_url.startswith('me.bluemail.mail://'):
                            logger.info("检测到重定向到自定义协议URL")
                            auth_code = self._extract_auth_code(next_url)
                            if auth_code:
                                logger.info(f"从自定义协议URL中提取到授权码: {auth_code[:15]}...")
                                return auth_code
                        
                        try:
                            # 发送GET请求
                            response = self.session.get(next_url, allow_redirects=False)
                            logger.info(f"重定向 {redirect_count+1} 状态码: {response.status_code}")
                            
                            # 如果是重定向，继续跟踪
                            if response.status_code in [301, 302, 303, 307, 308]:
                                redirect_count += 1
                                next_url = response.headers.get('Location')
                                if not next_url:
                                    logger.error("重定向URL为空，中断重定向链")
                                    break
                            else:
                                break
                        except requests.exceptions.InvalidSchema as e:
                            # 处理自定义协议异常
                            invalid_url = str(e).split("'")[1]
                            logger.info(f"检测到无效协议URL: {invalid_url}")
                            
                            if 'me.bluemail.mail://' in invalid_url and 'code=' in invalid_url:
                                auth_code = self._extract_auth_code(invalid_url)
                                if auth_code:
                                    logger.info(f"从自定义协议URL中提取到授权码: {auth_code[:15]}...")
                                    return auth_code
                            break
                else:
                    # 允许重定向的版本，将捕获最后一个响应
                    # 这种方法可能会在遇到自定义协议时失败
                    try:
                        consent_response = self.session.post(form_action, data=form_data, headers=consent_headers, allow_redirects=True)
                        final_url = consent_response.url
                        headers = {
                            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Thunderbird/128.2.3',
                            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
                            'accept-language': 'en-US,en;q=0.5',
                            'upgrade-insecure-requests': '1',
                            'sec-fetch-dest': 'document',
                            'sec-fetch-mode': 'navigate',
                            'sec-fetch-site': 'cross-site',
                            'priority': 'u=0, i',
                        }
                        logger.info(f"同意请求最终状态码: {consent_response.status_code}")
                        logger.info(f"同意请求最终URL: {final_url}")
                        if 'https://account.live.com/proofs/Add' in final_url:
                            canary = consent_response.text.split('id="canary" name="canary" value="')[1].split('"')[0]
                            data = {
                                'iProofOptions': 'Email',
                                'DisplayPhoneCountryISO': 'US',
                                'DisplayPhoneNumber': '',
                                'EmailAddress': '',
                                'canary': canary,
                                'action': 'Skip',
                                'PhoneNumber': '',
                                'PhoneCountryISO': '',
                            }
                            params = {
                                "client_id": self.CLIENT_ID,
                                "response_type": "code",
                                "redirect_uri": self.REDIRECT_URI,
                                "scope": " ".join(self.SCOPES),
                                "login_hint": self.email,
                            }
                            response = self.session.post(
                                'https://account.live.com/proofs/Add',
                                params=params,
                                headers=headers,
                                data=data,
                                allow_redirects=False
                            )
                        
                        # 检查最终URL是否包含授权码
                        if 'code=' in final_url:
                            auth_code = self._extract_auth_code(final_url)
                            if auth_code:
                                logger.info(f"从同意响应URL中提取到授权码")
                                return auth_code
                    except requests.exceptions.InvalidSchema as e:
                        # 处理自定义协议异常
                        invalid_url = str(e).split("'")[1]
                        logger.info(f"检测到无效协议URL: {invalid_url}")
                        
                        if 'me.bluemail.mail://' in invalid_url and 'code=' in invalid_url:
                            auth_code = self._extract_auth_code(invalid_url)
                            if auth_code:
                                logger.info(f"从自定义协议URL中提取到授权码: {auth_code[:15]}...")
                                return auth_code
                
                # 检查响应内容是否包含授权码重定向
                js_redirect_url = self._find_js_redirect(consent_response.text)
                if js_redirect_url:
                    logger.info(f"发现JavaScript重定向: {js_redirect_url}")
                    
                    # 确保是完整URL
                    if not js_redirect_url.startswith('http'):
                        if js_redirect_url.startswith('/'):
                            base_url = self._get_origin(consent_response.url)
                            js_redirect_url = base_url + js_redirect_url
                        else:
                            base_url = self._get_origin(consent_response.url)
                            js_redirect_url = base_url + '/' + js_redirect_url
                    
                    # 检查重定向URL是否包含代码
                    if 'code=' in js_redirect_url:
                        auth_code = self._extract_auth_code(js_redirect_url)
                        if auth_code:
                            logger.info(f"从JavaScript重定向URL中提取到授权码")
                            return auth_code
                    
                    # 检查是否重定向到自定义协议URL
                    if js_redirect_url.startswith('me.bluemail.mail://'):
                        logger.info("发现JavaScript重定向到自定义协议URL")
                        auth_code = self._extract_auth_code(js_redirect_url)
                        if auth_code:
                            logger.info(f"从JavaScript重定向到自定义协议URL中提取到授权码")
                            return auth_code
                    
                    # 跟随重定向
                    try:
                        logger.info(f"跟随JavaScript重定向...")
                        redirect_response = self.session.get(js_redirect_url, allow_redirects=False)
                        
                        # 检查是否有进一步的重定向
                        if redirect_response.status_code in [301, 302, 303, 307, 308]:
                            next_url = redirect_response.headers.get('Location')
                            logger.info(f"进一步重定向到: {next_url}")
                            
                            # 检查是否重定向到自定义协议URL
                            if next_url.startswith('me.bluemail.mail://'):
                                auth_code = self._extract_auth_code(next_url)
                                if auth_code:
                                    logger.info(f"从自定义协议URL中提取到授权码")
                                    return auth_code
                    except requests.exceptions.InvalidSchema as e:
                        # 处理自定义协议异常
                        invalid_url = str(e).split("'")[1]
                        logger.info(f"检测到无效协议URL: {invalid_url}")
                        
                        if 'me.bluemail.mail://' in invalid_url and 'code=' in invalid_url:
                            auth_code = self._extract_auth_code(invalid_url)
                            if auth_code:
                                logger.info(f"从自定义协议URL中提取到授权码: {auth_code[:15]}...")
                                return auth_code
            except requests.exceptions.InvalidSchema as e:
                # 处理自定义协议异常
                invalid_url = str(e).split("'")[1]
                logger.info(f"检测到无效协议URL: {invalid_url}")
                
                if 'me.bluemail.mail://' in invalid_url and 'code=' in invalid_url:
                    auth_code = self._extract_auth_code(invalid_url)
                    if auth_code:
                        logger.info(f"从自定义协议URL中提取到授权码: {auth_code[:15]}...")
                        return auth_code
            except Exception as e:
                logger.error(f"同意请求过程中出错: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
            
            logger.error("所有同意处理方法都未能获取授权码")
            return None
            
        except Exception as e:
            logger.error(f"处理同意页面时出错: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _find_js_redirect(self, html):
        """从HTML中查找JavaScript重定向URL"""
        # 尝试多种模式匹配JavaScript重定向
        js_redirect_patterns = [
            r'window\.location(?:\.href)?\s*=\s*[\'"]([^\'"]+=)[\'"]\s*\+\s*(?:encodeURIComponent\()?\s*[\'"]([^\'"]+)[\'"]\)?',
            r'window\.location(?:\.href)?\s*=\s*[\'"]([^\'"]*)[\'"]\s*;',
            r'window\.location\.replace\([\'"]([^\'"]*)[\'"]\)',
            r'self\.location\s*=\s*[\'"]([^\'"]*)[\'"]\s*;',
            r'location\.href\s*=\s*[\'"]([^\'"]*)[\'"]\s*;',
            r'location\.replace\([\'"]([^\'"]*)[\'"]\)',
            r'navigate\(\s*[\'"]([^\'"]*)[\'"]\s*\)',
            r'window\.navigate\(\s*[\'"]([^\'"]*)[\'"]\s*\)',
            r'document\.location\s*=\s*[\'"]([^\'"]*)[\'"]\s*;'
        ]
        
        for pattern in js_redirect_patterns:
            match = re.search(pattern, html)
            if match:
                # 根据捕获组数量构建URL
                if len(match.groups()) > 1:
                    return match.group(1) + match.group(2)
                return match.group(1)
        
        # 尝试从form中查找可能的下一个URL
        soup = BeautifulSoup(html, 'html.parser')
        form = soup.find('form')
        if form and form.get('action'):
            return form.get('action')
        
        return None
    
    def _follow_redirects(self, initial_url, max_redirects=10):
        """手动跟随重定向链"""
        current_url = initial_url
        redirect_count = 0
        
        while redirect_count < max_redirects:
            logger.info(f"跟随重定向 {redirect_count+1}: {current_url}")
            
            # 检查当前URL是否包含授权码
            if 'code=' in current_url:
                auth_code = self._extract_auth_code(current_url)
                logger.info(f"从重定向URL中获取到授权码: {auth_code[:15]}...")
                return self._get_token_from_code(auth_code)
            
            # 发送GET请求
            response = self.session.get(current_url, allow_redirects=False)
            logger.info(f"重定向 {redirect_count+1} 状态码: {response.status_code}")
            
            # 如果是重定向，继续跟踪
            if response.status_code in [301, 302, 303, 307, 308]:
                redirect_count += 1
                current_url = response.headers.get('Location')
                if not current_url:
                    logger.error("重定向URL为空，中断重定向链")
                    break
            else:
                # 检查最终响应中是否包含同意页面
                if 'consent' in response.text.lower():
                    logger.info("重定向到同意页面，处理同意流程...")
                    auth_code = self._handle_consent(response)
                    if auth_code:
                        return self._get_token_from_code(auth_code)
                    return None
                
                # 检查最终URL是否包含授权码
                if 'code=' in response.url:
                    auth_code = self._extract_auth_code(response.url)
                    logger.info(f"从最终URL中获取到授权码: {auth_code[:15]}...")
                    return self._get_token_from_code(auth_code)
                
                # 检查响应内容是否有错误
                error_message = self._extract_error_message(response.text)
                if error_message:
                    logger.error(f"重定向过程中出现错误: {error_message}")
                    return None
                
                logger.error("重定向链结束，但未找到授权码")
                break
        
        if redirect_count >= max_redirects:
            logger.error("达到最大重定向次数，中断重定向链")
        
        return None
    
    def _get_token_from_code(self, auth_code):
        if not auth_code:
            logger.error("授权码为空，无法请求令牌")
            return None
        
        logger.info("成功获取授权码，开始获取刷新令牌...")
        
        # 配置代理
        if self.proxy:
            # 格式化代理地址
            proxy_dict = {
                "http": self.proxy,
                "https": self.proxy
            }
            # 更新会话的代理设置
            self.session.proxies.update(proxy_dict)
            self.session.trust_env = True
            logger.info(f"使用代理获取令牌: {self.proxy}")
        else:
            # 如果没有代理，则使用直连
            self.session.proxies.clear()
            self.session.trust_env = False
            logger.info("使用直连方式获取令牌")
        
        # 使用与获取授权码完全相同的重定向URI
        redirect_uri = self.REDIRECT_URI
        
        # 使用与授权请求匹配的token endpoint
        token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
        
        # 构建令牌请求数据
        token_data = {
            'client_id': self.CLIENT_ID,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
            'code': auth_code,
            'scope': " ".join(self.SCOPES)
        }
        
        # 设置请求头
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
        }
        
        logger.info("开始使用授权码请求刷新令牌...")
        
        # 发送请求
        try:
            # 使用会话对象发送请求，确保不使用代理
            response = self.session.post(token_url, data=token_data, headers=headers)
            logger.info(f"令牌请求状态码: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                
                # 提取访问令牌和刷新令牌
                access_token = token_data.get('access_token')
                refresh_token = token_data.get('refresh_token')
                
                if refresh_token:
                    logger.success(f"成功获取刷新令牌: {refresh_token[:15]}...")
                    
                    # 将刷新令牌保存到实例
                    self.auth_data["refresh_token"] = refresh_token
                    
                    logger.success("刷新令牌已按格式保存到refresh_token.txt")
                    
                    return refresh_token
                else:
                    logger.error("响应中没有刷新令牌")
            else:
                logger.error(f"令牌请求失败: {response.text}")
        except Exception as e:
            logger.error(f"请求令牌时出错: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        
        return None

def get_refresh_token(email, password, proxy=None, no_verify=False):
    try:
        if not email or not password:
            return None
        
        client = BlueMailOAuthClient(email, password)
        
        if proxy:
            client.set_proxy(proxy)
        
        if no_verify:
            client.session.verify = False
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        refresh_token = client.execute_auth_flow()
                
        return refresh_token
            
    except KeyboardInterrupt:
        return None
    except Exception as e:
        return None
