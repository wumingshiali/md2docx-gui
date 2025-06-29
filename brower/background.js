chrome.webRequest.onBeforeRequest.addListener(
  function (details) {
    // 检查 URL 是否以 .md 结尾
    if (details.url.endsWith(".md")) {
      console.log("拦截到 Markdown 文件下载:", details.url);

      // 构造跳转地址
      const redirectUrl = `http://localhost:2403?url=${encodeURIComponent(details.url)}`;

      // 阻止原下载并跳转
      return { redirectUrl: redirectUrl };
    }
    return {}; // 不影响其他请求
  },
  {
    urls: ["<all_urls>"],
    types: ["main_frame"] // 只拦截主框架导航（即点击下载链接）
  },
  ["blocking"]
);