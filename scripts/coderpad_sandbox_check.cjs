// Re-runnable check that the kit works in CoderPad's public sandbox (no login): opens a Python Project,
// clones the kit, runs check.sh and the agent tests, fetches KIT.md, and saves kit_terminal.png.
// Run: PLAYWRIGHT_MODULE=<path to playwright> CHROME_PATH=<chromium binary, optional> node scripts/coderpad_sandbox_check.cjs
// Clicks use fixed screen positions in CoderPad's current layout; a layout change breaks them loudly (timeout).
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
(async () => {
  const b = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {});
  const p = await b.newPage({ viewport: { width: 1500, height: 950 } });
  await p.goto('https://app.coderpad.io/sandbox', { waitUntil: 'domcontentloaded', timeout: 45000 });
  await p.waitForTimeout(10000);
  await p.mouse.click(30, 128);
  await p.waitForTimeout(1500);
  await p.getByText('Switch Language').click();
  await p.waitForTimeout(2000);
  await p.keyboard.type('Python');
  await p.waitForTimeout(1500);
  await p.getByText('Python Project (Recommended)').first().click();
  await p.waitForTimeout(40000);
  await p.waitForTimeout(10000);
  await p.mouse.click(600, 800);
  const cmds = ['git clone -q --depth 1 https://github.com/BrianMills2718/interview-kit kit && ls kit',
    'cp kit/PLAN.template.md PLAN.md; bash kit/check.sh 2>&1 | tail -4',
    'pip install -q pytest langgraph langchain-core 2>&1 | tail -1; cd kit && python3 -m pytest -q tests/test_agent_template.py 2>&1 | tail -2; cd ..',
    'curl -s https://raw.githubusercontent.com/BrianMills2718/interview-kit/main/KIT.md | head -3'];
  for (const c of cmds) { await p.keyboard.type(c, { delay: 25 }); await p.keyboard.press('Enter'); await p.waitForTimeout(c.startsWith('pip') ? 60000 : 12000); }
  await p.screenshot({ path: 'kit_terminal.png' });
  const t = await p.locator('.xterm-rows').last().innerText().catch(e => 'noxterm ' + e.message);
  console.log('TERM', t);
  console.log('EXPLORER', (await p.innerText('body')).replace(/\s+/g,' ').slice(0, 300));
  await b.close();
})();
