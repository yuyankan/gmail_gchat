// setup.js
const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: false }); // 必须在有头模式下手动登录
  const context = await browser.newContext();
  const page = await context.newPage();

  // 导航到 Power BI 登录页面
  console.log('请在打开的浏览器窗口中手动登录 Power BI...');
  await page.goto('https://app.powerbi.com/');

  // 等待用户手动登录成功，可以延长超时时间
  // 你可以判断某个登录后的特定元素来确认登录成功
  // 这里我们简单地等待用户完成操作
  console.log('登录成功后，请不要关闭浏览器，脚本将自动保存认证状态...');
  await page.waitForSelector('div[data-testid="workspace-switcher-button"]', { timeout: 300000 }); // 等待主页加载完成，超时5分钟

  // 保存认证状态到文件
  const storageState = await context.storageState();
  fs.writeFileSync('auth.json', JSON.stringify(storageState, null, 2));

  console.log('认证状态已成功保存到 auth.json 文件！');
  await browser.close();
})();