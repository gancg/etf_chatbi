"""
ETF ChatBI 助手 - 邮件通知模块
用于发送价格波动提醒邮件
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


class EmailNotifier:
    """邮件通知器"""
    
    def __init__(self):
        """初始化邮件通知器,从环境变量读取配置"""
        self.smtp_server = os.getenv('EMAIL_SMTP_SERVER', 'smtp.qq.com')
        self.smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '465'))
        self.sender = os.getenv('EMAIL_SENDER', '')
        self.password = os.getenv('EMAIL_PASSWORD', '')
        self.receivers = os.getenv('EMAIL_RECEIVER', '').split(',')
        
        # 清理收件人列表
        self.receivers = [email.strip() for email in self.receivers if email.strip()]
    
    def is_configured(self):
        """
        检查邮件配置是否完整
        
        Returns:
            bool: 配置是否完整
        """
        return all([
            self.smtp_server,
            self.smtp_port,
            self.sender,
            self.password,
            self.receivers
        ])
    
    def send_price_alert(self, etf_code, etf_name, current_price, previous_price, change_percent):
        """
        发送价格波动提醒邮件
        
        Args:
            etf_code: ETF代码
            etf_name: ETF名称
            current_price: 当前收盘价
            previous_price: 前一日收盘价
            change_percent: 涨跌幅百分比
            
        Returns:
            bool: 发送是否成功
        """
        if not self.is_configured():
            print("警告: 邮件配置不完整,跳过发送")
            return False
        
        # 判断涨跌方向
        direction = "上涨" if change_percent > 0 else "下跌"
        abs_change = abs(change_percent)
        
        # 构建邮件主题
        subject = f"[ETF提醒] {etf_name} 今日{direction}达到 {abs_change:.2f}%"
        
        # 构建邮件正文
        body = self._build_email_body(
            etf_code, etf_name, current_price, 
            previous_price, change_percent, direction
        )
        
        # 发送邮件
        return self._send_email(subject, body)
    
    def _build_email_body(self, etf_code, etf_name, current_price, previous_price, change_percent, direction):
        """
        构建邮件正文
        
        Args:
            etf_code: ETF代码
            etf_name: ETF名称
            current_price: 当前收盘价
            previous_price: 前一日收盘价
            change_percent: 涨跌幅百分比
            direction: 涨跌方向
            
        Returns:
            str: HTML格式的邮件正文
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html_body = f"""
        <html>
        <body>
            <h2 style="color: {'red' if change_percent > 0 else 'green'}">
                ETF价格波动提醒
            </h2>
            
            <table border="1" cellpadding="10" cellspacing="0" style="border-collapse: collapse;">
                <tr>
                    <th style="background-color: #f2f2f2;">项目</th>
                    <th style="background-color: #f2f2f2;">详情</th>
                </tr>
                <tr>
                    <td>ETF代码</td>
                    <td>{etf_code}</td>
                </tr>
                <tr>
                    <td>ETF名称</td>
                    <td>{etf_name}</td>
                </tr>
                <tr>
                    <td>前一日收盘价</td>
                    <td>{previous_price:.2f} 元</td>
                </tr>
                <tr>
                    <td>当日收盘价</td>
                    <td>{current_price:.2f} 元</td>
                </tr>
                <tr>
                    <td>涨跌幅</td>
                    <td style="color: {'red' if change_percent > 0 else 'green'}; font-weight: bold;">
                        {direction} {abs(change_percent):.2f}%
                    </td>
                </tr>
                <tr>
                    <td>触发时间</td>
                    <td>{timestamp}</td>
                </tr>
            </table>
            
            <p style="margin-top: 20px; color: #666;">
                此邮件由 ETF ChatBI 助手自动发送
            </p>
        </body>
        </html>
        """
        
        return html_body
    
    def _send_email(self, subject, body):
        """
        发送邮件
        
        Args:
            subject: 邮件主题
            body: 邮件正文(HTML格式)
            
        Returns:
            bool: 发送是否成功
        """
        try:
            # 创建邮件对象
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender
            msg['To'] = ', '.join(self.receivers)
            msg['Subject'] = subject
            
            # 添加HTML内容
            html_part = MIMEText(body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 连接SMTP服务器并发送
            if self.smtp_port == 465:
                # SSL连接
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                # 普通连接
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            
            server.login(self.sender, self.password)
            server.sendmail(self.sender, self.receivers, msg.as_string())
            server.quit()
            
            print(f"邮件发送成功: {subject}")
            return True
            
        except Exception as e:
            print(f"邮件发送失败: {str(e)}")
            return False
    
    def check_and_notify(self, etf_data_list, threshold=5.0):
        """
        检查ETF价格波动并发送通知
        
        Args:
            etf_data_list: ETF数据列表,每个元素为dict:
                {
                    'ts_code': 股票代码,
                    'ts_name': 股票名称,
                    'current_close': 当日收盘价,
                    'previous_close': 前一日收盘价
                }
            threshold: 触发阈值(默认5%)
            
        Returns:
            list: 已发送通知的ETF列表
        """
        notified_etfs = []
        
        for etf in etf_data_list:
            current = etf['current_close']
            previous = etf['previous_close']
            
            if previous == 0:
                continue
            
            # 计算涨跌幅
            change_percent = ((current - previous) / previous) * 100
            
            # 检查是否超过阈值
            if abs(change_percent) >= threshold:
                success = self.send_price_alert(
                    etf['ts_code'],
                    etf['ts_name'],
                    current,
                    previous,
                    change_percent
                )
                
                if success:
                    notified_etfs.append({
                        **etf,
                        'change_percent': change_percent
                    })
        
        return notified_etfs


if __name__ == '__main__':
    # 测试邮件发送
    notifier = EmailNotifier()
    
    if notifier.is_configured():
        print("邮件配置完整,开始测试...")
        
        # 模拟ETF数据
        test_data = [
            {
                'ts_code': '512400',
                'ts_name': '有色金属ETF南方',
                'current_close': 1.05,
                'previous_close': 1.00
            }
        ]
        
        # 检查并发送通知
        notified = notifier.check_and_notify(test_data, threshold=5.0)
        
        if notified:
            print(f"\n已发送 {len(notified)} 封通知邮件:")
            for item in notified:
                print(f"  - {item['ts_name']}: {item['change_percent']:.2f}%")
        else:
            print("\n没有ETF达到触发阈值")
    else:
        print("邮件配置不完整,请设置以下环境变量:")
        print("  - EMAIL_SMTP_SERVER")
        print("  - EMAIL_SMTP_PORT")
        print("  - EMAIL_SENDER")
        print("  - EMAIL_PASSWORD")
        print("  - EMAIL_RECEIVER")
